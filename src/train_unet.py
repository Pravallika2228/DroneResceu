import os
import numpy as np
import tensorflow as tf
from PIL import Image

# ==========================================
# SETTINGS
# ==========================================
IMG_SIZE = 256
NUM_CLASSES = 10
BATCH_SIZE = 4
EPOCHS = 10

DATASET = "dataset/FloodNet/FloodNet-Supervised_v1.0"

TRAIN_IMG_DIR = os.path.join(
    DATASET, "train", "train-org-img"
)

TRAIN_MASK_DIR = os.path.join(
    DATASET, "train", "train-label-img"
)

VAL_IMG_DIR = os.path.join(
    DATASET, "val", "val-org-img"
)

VAL_MASK_DIR = os.path.join(
    DATASET, "val", "val-label-img"
)

MODEL_DIR = "models/unet_weighted"

os.makedirs(MODEL_DIR, exist_ok=True)


# ==========================================
# CLASS NAMES
# ==========================================
CLASS_NAMES = [
    "Background",
    "Building Flooded",
    "Building Non-Flooded",
    "Road Flooded",
    "Road Non-Flooded",
    "Water",
    "Tree",
    "Vehicle",
    "Pool",
    "Grass"
]


# ==========================================
# GET IMAGE/MASK PAIRS
# ==========================================
def get_pairs(image_dir, mask_dir):

    images = sorted([
        f for f in os.listdir(image_dir)
        if f.lower().endswith(
            (".jpg", ".jpeg", ".png")
        )
    ])

    pairs = []

    for image_name in images:

        base = os.path.splitext(image_name)[0]

        mask_name = base + "_lab.png"

        mask_path = os.path.join(
            mask_dir,
            mask_name
        )

        if os.path.exists(mask_path):

            pairs.append((
                os.path.join(
                    image_dir,
                    image_name
                ),
                mask_path
            ))

    return pairs


train_pairs = get_pairs(
    TRAIN_IMG_DIR,
    TRAIN_MASK_DIR
)

val_pairs = get_pairs(
    VAL_IMG_DIR,
    VAL_MASK_DIR
)

print("Training pairs  :", len(train_pairs))
print("Validation pairs:", len(val_pairs))


# ==========================================
# DATA LOADER
# ==========================================
def load_data(image_path, mask_path):

    image = Image.open(
        image_path
    ).convert("RGB")

    image = image.resize(
        (IMG_SIZE, IMG_SIZE),
        Image.Resampling.BILINEAR
    )

    image = (
        np.array(image)
        .astype(np.float32)
        / 255.0
    )

    mask = Image.open(
        mask_path
    )

    # IMPORTANT:
    # NEAREST keeps segmentation class IDs intact
    mask = mask.resize(
        (IMG_SIZE, IMG_SIZE),
        Image.Resampling.NEAREST
    )

    mask = np.array(
        mask
    ).astype(np.int32)

    return image, mask


# ==========================================
# TF DATASET
# ==========================================
def generator(pairs):

    for image_path, mask_path in pairs:

        image, mask = load_data(
            image_path,
            mask_path
        )

        yield image, mask


def create_dataset(
    pairs,
    shuffle=False
):

    dataset = tf.data.Dataset.from_generator(
        lambda: generator(pairs),

        output_signature=(
            tf.TensorSpec(
                shape=(IMG_SIZE, IMG_SIZE, 3),
                dtype=tf.float32
            ),

            tf.TensorSpec(
                shape=(IMG_SIZE, IMG_SIZE),
                dtype=tf.int32
            )
        )
    )

    if shuffle:

        dataset = dataset.shuffle(
            buffer_size=500,
            reshuffle_each_iteration=True
        )

    dataset = dataset.batch(
        BATCH_SIZE
    )

    dataset = dataset.prefetch(
        tf.data.AUTOTUNE
    )

    return dataset


train_dataset = create_dataset(
    train_pairs,
    shuffle=True
)

val_dataset = create_dataset(
    val_pairs,
    shuffle=False
)


# ==========================================
# CLASS WEIGHTS
# ==========================================
# Based on the training-pixel distribution
# observed from FloodNet.

CLASS_WEIGHTS = np.array([
    1.0,   # Background
    2.0,   # Building Flooded
    1.2,   # Building Non-Flooded
    2.0,   # Road Flooded
    0.8,   # Road Non-Flooded
    0.7,   # Water
    0.6,   # Tree
    4.0,   # Vehicle
    4.0,   # Pool
    0.3    # Grass
], dtype=np.float32)

print("\nClass weights:")

for i in range(NUM_CLASSES):

    print(
        f"{i:2d} "
        f"{CLASS_NAMES[i]:22s} "
        f"{CLASS_WEIGHTS[i]:.2f}"
    )


# ==========================================
# CLASS-WEIGHTED LOSS
# ==========================================
def weighted_sparse_categorical_crossentropy(
    y_true,
    y_pred
):

    y_true = tf.cast(
        y_true,
        tf.int32
    )

    # Standard sparse categorical CE
    pixel_loss = tf.keras.losses.sparse_categorical_crossentropy(
        y_true,
        y_pred,
        from_logits=False
    )

    # Get weight for every pixel according
    # to its ground-truth class
    weights = tf.gather(
        tf.constant(
            CLASS_WEIGHTS,
            dtype=tf.float32
        ),
        y_true
    )

    weighted_loss = (
        pixel_loss * weights
    )

    return tf.reduce_mean(
        weighted_loss
    )


# ==========================================
# U-NET
# ==========================================
def conv_block(x, filters):

    x = tf.keras.layers.Conv2D(
        filters,
        3,
        padding="same",
        activation="relu"
    )(x)

    x = tf.keras.layers.Conv2D(
        filters,
        3,
        padding="same",
        activation="relu"
    )(x)

    return x


def build_unet():

    inputs = tf.keras.Input(
        shape=(IMG_SIZE, IMG_SIZE, 3)
    )

    # Encoder
    c1 = conv_block(
        inputs,
        16
    )

    p1 = tf.keras.layers.MaxPooling2D()(c1)

    c2 = conv_block(
        p1,
        32
    )

    p2 = tf.keras.layers.MaxPooling2D()(c2)

    c3 = conv_block(
        p2,
        64
    )

    p3 = tf.keras.layers.MaxPooling2D()(c3)

    c4 = conv_block(
        p3,
        128
    )

    p4 = tf.keras.layers.MaxPooling2D()(c4)

    # Bottleneck
    c5 = conv_block(
        p4,
        256
    )

    # Decoder
    u6 = tf.keras.layers.UpSampling2D()(c5)

    u6 = tf.keras.layers.Concatenate()([
        u6,
        c4
    ])

    c6 = conv_block(
        u6,
        128
    )

    u7 = tf.keras.layers.UpSampling2D()(c6)

    u7 = tf.keras.layers.Concatenate()([
        u7,
        c3
    ])

    c7 = conv_block(
        u7,
        64
    )

    u8 = tf.keras.layers.UpSampling2D()(c7)

    u8 = tf.keras.layers.Concatenate()([
        u8,
        c2
    ])

    c8 = conv_block(
        u8,
        32
    )

    u9 = tf.keras.layers.UpSampling2D()(c8)

    u9 = tf.keras.layers.Concatenate()([
        u9,
        c1
    ])

    c9 = conv_block(
        u9,
        16
    )

    # 10 FloodNet classes
    outputs = tf.keras.layers.Conv2D(
        NUM_CLASSES,
        1,
        activation="softmax"
    )(c9)

    return tf.keras.Model(
        inputs,
        outputs
    )


model = build_unet()

print("\nU-Net model created.")

print(
    "Output shape:",
    model.output_shape
)


# ==========================================
# COMPILE
# ==========================================
model.compile(

    optimizer=tf.keras.optimizers.Adam(
        learning_rate=0.0005
    ),

    loss=weighted_sparse_categorical_crossentropy,

    metrics=[
        "sparse_categorical_accuracy"
    ]
)


# ==========================================
# CALLBACKS
# ==========================================
callbacks = [

    tf.keras.callbacks.ModelCheckpoint(

        os.path.join(
            MODEL_DIR,
            "unet_best.keras"
        ),

        monitor="val_loss",

        save_best_only=True
    ),

    tf.keras.callbacks.EarlyStopping(

        monitor="val_loss",

        patience=3,

        restore_best_weights=True
    ),

    tf.keras.callbacks.ReduceLROnPlateau(

        monitor="val_loss",

        factor=0.5,

        patience=2,

        min_lr=1e-6
    )
]


# ==========================================
# TRAIN
# ==========================================
print(
    "\nStarting class-weighted U-Net training...\n"
)

history = model.fit(

    train_dataset,

    validation_data=val_dataset,

    epochs=EPOCHS,

    callbacks=callbacks
)


# ==========================================
# SAVE FINAL MODEL
# ==========================================
final_model_path = os.path.join(
    MODEL_DIR,
    "unet_final.keras"
)

model.save(
    final_model_path
)


print("\n====================================")
print("WEIGHTED U-NET TRAINING COMPLETED")
print("====================================")

print(
    "Best model :",
    os.path.join(
        MODEL_DIR,
        "unet_best.keras"
    )
)

print(
    "Final model:",
    final_model_path
)