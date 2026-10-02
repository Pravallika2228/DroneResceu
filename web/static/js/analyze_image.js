(() => {

    "use strict";


    const input =
        document.getElementById(
            "analyzeInput"
        );

    const drop =
        document.getElementById(
            "analyzeDropzone"
        );

    const wrap =
        document.getElementById(
            "analyzePreviewWrap"
        );

    const img =
        document.getElementById(
            "analyzePreview"
        );

    const name =
        document.getElementById(
            "analyzeFilename"
        );

    const button =
        document.getElementById(
            "runAnalysisButton"
        );

    const status =
        document.getElementById(
            "analyzeStatus"
        );


    if (
        !input ||
        !drop ||
        !wrap ||
        !img ||
        !name ||
        !button ||
        !status
    ) {

        return;

    }


    let selectedFile =
        null;


    // ============================================================
    // SELECT IMAGE
    // ============================================================

    drop.addEventListener(
        "click",
        () => {

            input.click();

        }
    );


    input.addEventListener(
        "change",
        () => {

            selectedFile =
                input.files[0] ||
                null;


            if (!selectedFile) {

                return;

            }


            img.src =
                URL.createObjectURL(
                    selectedFile
                );


            name.textContent =
                selectedFile.name;


            wrap.hidden =
                false;


            status.textContent =
                "Image selected. Ready to analyze.";

        }
    );


    // ============================================================
    // RUN ANALYSIS
    // ============================================================

    button.addEventListener(
        "click",
        async () => {

            if (!selectedFile) {

                status.textContent =
                    "Please select an image first.";

                return;

            }


            button.disabled =
                true;

            button.textContent =
                "ANALYZING...";


            status.textContent =
                "Running AI analysis. Please wait...";


            const formData =
                new FormData();


            formData.append(
                "image",
                selectedFile
            );


            try {

                const response =
                    await fetch(
                        "/analyze",
                        {
                            method:
                                "POST",

                            body:
                                formData
                        }
                    );


                const contentType =
                    response.headers.get(
                        "content-type"
                    ) || "";


                if (
                    !contentType.includes(
                        "application/json"
                    )
                ) {

                    throw new Error(
                        "Server returned an unexpected page. Please sign in again."
                    );

                }


                const data =
                    await response.json();


                if (
                    !response.ok ||
                    !data.success
                ) {

                    throw new Error(
                        data.error ||
                        "Analysis failed."
                    );

                }


                // ==================================================
                // CURRENT BACKEND STRUCTURE
                //
                // data.result
                //      ↓
                // assessment
                //      ↓
                // flood_detected
                // flood_severity
                // rescue_priority
                // ==================================================

                const result =
                    data.result || {};


                const report =
                    result.assessment ||
                    data.assessment ||
                    {};


                status.innerHTML = `

                    <strong>
                        Analysis completed.
                    </strong>

                    Flood:
                    <strong>
                        ${escapeHtml(
                            report.flood_detected ||
                            "--"
                        )}
                    </strong>

                    • Severity:
                    <strong>
                        ${escapeHtml(
                            report.flood_severity ||
                            "--"
                        )}
                    </strong>

                    • Priority:
                    <strong>
                        ${escapeHtml(
                            report.rescue_priority ||
                            "--"
                        )}
                    </strong>

                    <br><br>

                    Flood Probability:
                    <strong>
                        ${Number(
                            report.flood_probability ??
                            0
                        ).toFixed(2)}%
                    </strong>

                    • Flood Coverage:
                    <strong>
                        ${Number(
                            report.flood_coverage ??
                            0
                        ).toFixed(2)}%
                    </strong>

                    <br><br>

                    <a
                        href="/dashboard"
                        class="primary-button"
                    >
                        OPEN DASHBOARD →
                    </a>

                `;


                // --------------------------------------------------
                // Save latest result for browser use
                // --------------------------------------------------

                try {

                    localStorage.setItem(
                        "droneRescueLatest",
                        JSON.stringify({

                            filename:
                                selectedFile.name,

                            report:
                                report,

                            vehicle_breakdown:
                                result.vehicle_breakdown ||
                                {},

                            segmentation_image:
                                result.segmentation_image ||
                                "",

                            pipeline:
                                result.pipeline ||
                                {},

                            analyzed_at:
                                new Date().toISOString()

                        })
                    );

                } catch (storageError) {

                    console.warn(
                        "Could not save latest result:",
                        storageError
                    );

                }


            } catch (error) {

                console.error(
                    "Analysis error:",
                    error
                );


                status.textContent =
                    error.message ||
                    "Analysis failed.";

            } finally {

                button.disabled =
                    false;

                button.textContent =
                    "RUN AI ANALYSIS";

            }

        }
    );


    // ============================================================
    // ESCAPE HTML
    // ============================================================

    function escapeHtml(
        value
    ) {

        return String(
            value ?? ""
        ).replace(
            /[&<>"']/g,
            character => ({

                "&": "&amp;",
                "<": "&lt;",
                ">": "&gt;",
                '"': "&quot;",
                "'": "&#039;"

            }[character])
        );

    }

})();