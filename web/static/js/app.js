(() => {

    "use strict";


    // ============================================================
    // THEME
    // ============================================================

    function applyTheme() {

        const theme =
            localStorage.getItem(
                "droneRescueTheme"
            ) || "dark";


        document.body.classList.toggle(
            "light",
            theme === "light"
        );

    }


    function setupTheme() {

        applyTheme();


        document
            .querySelectorAll(
                "[data-theme-toggle]"
            )
            .forEach(
                button => {

                    button.addEventListener(
                        "click",
                        () => {

                            const isLight =
                                !document.body
                                    .classList
                                    .contains(
                                        "light"
                                    );


                            document.body
                                .classList
                                .toggle(
                                    "light",
                                    isLight
                                );


                            localStorage.setItem(
                                "droneRescueTheme",
                                isLight
                                    ? "light"
                                    : "dark"
                            );

                        }
                    );

                }
            );

    }


    // ============================================================
    // SETTINGS MODAL
    // ============================================================

    const modal =
        document.getElementById(
            "settingsModal"
        );

    const content =
        document.getElementById(
            "modalContent"
        );

    const closeButton =
        document.getElementById(
            "closeSettingsModal"
        );


    function closeModal() {

        if (!modal) {
            return;
        }


        if (
            document.activeElement &&
            modal.contains(
                document.activeElement
            )
        ) {

            document.activeElement.blur();

        }


        modal.hidden = true;

        modal.setAttribute(
            "aria-hidden",
            "true"
        );


        if (content) {

            content.innerHTML = "";

        }

    }


    function openModal(
        html
    ) {

        if (
            !modal ||
            !content
        ) {

            return;

        }


        content.innerHTML =
            html;


        modal.hidden =
            false;


        modal.setAttribute(
            "aria-hidden",
            "false"
        );


        requestAnimationFrame(
            () => {

                const first =
                    content.querySelector(
                        "input, button, select, textarea"
                    );


                if (first) {

                    first.focus();

                }

            }
        );

    }


    closeButton?.addEventListener(
        "click",
        closeModal
    );


    modal?.addEventListener(
        "click",
        event => {

            if (
                event.target === modal
            ) {

                closeModal();

            }

        }
    );


    document.addEventListener(
        "keydown",
        event => {

            if (
                event.key === "Escape" &&
                modal &&
                !modal.hidden
            ) {

                closeModal();

            }

        }
    );


    // ============================================================
    // SAFE JSON FETCH
    // ============================================================

    async function fetchJson(
        url,
        options = {}
    ) {

        const response =
            await fetch(
                url,
                options
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
                "Request failed."
            );

        }


        return data;

    }


    // ============================================================
    // MANAGE ACCOUNT
    // ============================================================

    document
        .getElementById(
            "manageAccount"
        )
        ?.addEventListener(
            "click",
            async () => {

                try {

                    const data =
                        await fetchJson(
                            "/api/account",
                            {
                                cache:
                                    "no-store"
                            }
                        );


                    openModal(`

                        <h2>
                            Manage Account
                        </h2>

                        <p class="muted">
                            Update the username shown in DroneRescue.
                        </p>

                        <label for="modalUsername">
                            Username
                        </label>

                        <input
                            id="modalUsername"
                            type="text"
                            value="${escapeHtml(
                                data.username || ""
                            )}"
                            autocomplete="username"
                        >

                        <button
                            class="primary-button"
                            id="saveAccount"
                            type="button"
                            style="margin-top:18px"
                        >
                            SAVE ACCOUNT
                        </button>

                    `);


                    document
                        .getElementById(
                            "saveAccount"
                        )
                        ?.addEventListener(
                            "click",
                            async () => {

                                const input =
                                    document.getElementById(
                                        "modalUsername"
                                    );


                                const username =
                                    input?.value
                                        .trim() || "";


                                if (!username) {

                                    alert(
                                        "Username cannot be empty."
                                    );

                                    return;

                                }


                                try {

                                    const result =
                                        await fetchJson(
                                            "/api/account",
                                            {
                                                method:
                                                    "POST",

                                                headers: {
                                                    "Content-Type":
                                                        "application/json"
                                                },

                                                body:
                                                    JSON.stringify({
                                                        username:
                                                            username
                                                    })
                                            }
                                        );


                                    alert(
                                        result.message ||
                                        "Account updated successfully."
                                    );


                                    closeModal();


                                    window.location.reload();

                                } catch (error) {

                                    alert(
                                        error.message
                                    );

                                }

                            }
                        );

                } catch (error) {

                    alert(
                        error.message
                    );

                }

            }
        );


    // ============================================================
    // CHANGE PASSWORD
    // ============================================================

    document
        .getElementById(
            "changePassword"
        )
        ?.addEventListener(
            "click",
            () => {

                openModal(`

                    <h2>
                        Change Password
                    </h2>

                    <p class="muted">
                        Update the password used by this demo application.
                    </p>

                    <label for="currentPassword">
                        Current Password
                    </label>

                    <input
                        id="currentPassword"
                        type="password"
                        autocomplete="current-password"
                    >

                    <label for="newPassword">
                        New Password
                    </label>

                    <input
                        id="newPassword"
                        type="password"
                        autocomplete="new-password"
                    >

                    <label for="confirmPassword">
                        Confirm New Password
                    </label>

                    <input
                        id="confirmPassword"
                        type="password"
                        autocomplete="new-password"
                    >

                    <button
                        class="primary-button"
                        id="savePassword"
                        type="button"
                        style="margin-top:18px"
                    >
                        UPDATE PASSWORD
                    </button>

                `);


                document
                    .getElementById(
                        "savePassword"
                    )
                    ?.addEventListener(
                        "click",
                        async () => {

                            const current =
                                document
                                    .getElementById(
                                        "currentPassword"
                                    )
                                    ?.value || "";


                            const next =
                                document
                                    .getElementById(
                                        "newPassword"
                                    )
                                    ?.value || "";


                            const confirm =
                                document
                                    .getElementById(
                                        "confirmPassword"
                                    )
                                    ?.value || "";


                            if (
                                !current ||
                                !next ||
                                !confirm
                            ) {

                                alert(
                                    "Please fill all password fields."
                                );

                                return;

                            }


                            if (
                                next.length < 4
                            ) {

                                alert(
                                    "New password must contain at least 4 characters."
                                );

                                return;

                            }


                            if (
                                next !== confirm
                            ) {

                                alert(
                                    "New password and confirmation do not match."
                                );

                                return;

                            }


                            try {

                                const result =
                                    await fetchJson(
                                        "/api/password",
                                        {
                                            method:
                                                "POST",

                                            headers: {
                                                "Content-Type":
                                                    "application/json"
                                            },

                                            body:
                                                JSON.stringify({
                                                    current_password:
                                                        current,

                                                    new_password:
                                                        next
                                                })
                                        }
                                    );


                                alert(
                                    result.message ||
                                    "Password updated successfully."
                                );


                                closeModal();

                            } catch (error) {

                                alert(
                                    error.message
                                );

                            }

                        }
                    );

            }
        );


    // ============================================================
    // LOGIN SESSION
    // ============================================================

    document
        .getElementById(
            "viewSessions"
        )
        ?.addEventListener(
            "click",
            async () => {

                try {

                    const data =
                        await fetchJson(
                            "/api/session",
                            {
                                cache:
                                    "no-store"
                            }
                        );


                    openModal(`

                        <h2>
                            Login Session
                        </h2>

                        <p class="muted">
                            Current signed-in session information.
                        </p>

                        <div class="status-box">

                            <strong>
                                Status:
                            </strong>

                            ${escapeHtml(
                                data.status
                            )}

                        </div>

                        <div class="status-box">

                            <strong>
                                User:
                            </strong>

                            ${escapeHtml(
                                data.username
                            )}

                        </div>

                        <div class="status-box">

                            <strong>
                                Remember Me:
                            </strong>

                            ${
                                data.remember_me
                                    ? "Enabled"
                                    : "Disabled"
                            }

                        </div>

                    `);

                } catch (error) {

                    alert(
                        error.message
                    );

                }

            }
        );


    // ============================================================
    // AI DISPLAY SETTINGS
    // ============================================================

    document
        .querySelectorAll(
            ".switch[data-setting]"
        )
        .forEach(
            button => {

                const key =
                    "droneRescue_" +
                    button.dataset.setting;


                const saved =
                    localStorage.getItem(
                        key
                    );


                if (
                    saved !== null
                ) {

                    button.classList.toggle(
                        "active",
                        saved === "true"
                    );

                }


                button.addEventListener(
                    "click",
                    () => {

                        button.classList.toggle(
                            "active"
                        );


                        localStorage.setItem(
                            key,
                            String(
                                button.classList
                                    .contains(
                                        "active"
                                    )
                            )
                        );

                    }
                );

            }
        );


    // ============================================================
    // REPORT RENDERING
    // ============================================================

    window.formatReport =
        function(report) {

            if (!report) {

                return `
                    <div class="empty-state">
                        No assessment available.
                    </div>
                `;

            }


            return `

                <div class="assessment-grid">

                    <div class="assessment-item">
                        <span>FLOOD STATUS</span>
                        <strong>
                            ${escapeHtml(
                                report.flood_detected ?? "--"
                            )}
                        </strong>
                    </div>

                    <div class="assessment-item">
                        <span>FLOOD SEVERITY</span>
                        <strong>
                            ${escapeHtml(
                                report.flood_severity ?? "--"
                            )}
                        </strong>
                    </div>

                    <div class="assessment-item">
                        <span>RESCUE PRIORITY</span>
                        <strong>
                            ${escapeHtml(
                                report.rescue_priority ?? "--"
                            )}
                        </strong>
                    </div>

                    <div class="assessment-item">
                        <span>PEOPLE VISIBLE</span>
                        <strong>
                            ${Number(
                                report.people_visible ?? 0
                            )}
                        </strong>
                    </div>

                    <div class="assessment-item">
                        <span>VEHICLES VISIBLE</span>
                        <strong>
                            ${Number(
                                report.vehicles_visible ?? 0
                            )}
                        </strong>
                    </div>

                </div>

                <div class="impact-block">

                    <h4>
                        FLOOD IMPACT
                    </h4>

                    <div>
                        Building Impact

                        <strong>
                            ${Number(
                                report.flooded_building_area ?? 0
                            ).toFixed(2)}%
                        </strong>
                    </div>

                    <div>
                        Road Impact

                        <strong>
                            ${Number(
                                report.flooded_road_area ?? 0
                            ).toFixed(2)}%
                        </strong>
                    </div>

                    <div>
                        Total Coverage

                        <strong>
                            ${Number(
                                report.flood_coverage ?? 0
                            ).toFixed(2)}%
                        </strong>
                    </div>

                </div>

            `;

        };


    // ============================================================
    // HISTORY
    // ============================================================

    window.renderRecords =
        function(
            records,
            targetId
        ) {

            const element =
                document.getElementById(
                    targetId
                );


            if (!element) {
                return;
            }


            if (
                !records.length
            ) {

                element.innerHTML = `
                    <div class="empty-state">
                        No completed analyses yet.
                    </div>
                `;

                return;

            }


            element.innerHTML =
                records.map(
                    record => {

                        const report =
                            record.report ||
                            {};


                        return `

                            <div class="record">

                                <img
                                    src="${escapeHtml(
                                        record.image_url || ""
                                    )}"
                                    alt="Analyzed drone image"
                                >

                                <div>

                                    <h3>
                                        ${escapeHtml(
                                            record.filename ||
                                            "Drone image"
                                        )}
                                    </h3>

                                    <p>
                                        ${escapeHtml(
                                            record.timestamp ||
                                            ""
                                        )}
                                    </p>

                                    <p>
                                        Flood:
                                        <strong>
                                            ${escapeHtml(
                                                report.flood_detected ||
                                                "--"
                                            )}
                                        </strong>

                                        &nbsp;

                                        Probability:
                                        ${Number(
                                            report.flood_probability ??
                                            0
                                        ).toFixed(2)}%
                                    </p>

                                    <p>
                                        Severity:
                                        <strong>
                                            ${escapeHtml(
                                                report.flood_severity ||
                                                "--"
                                            )}
                                        </strong>

                                        &nbsp;

                                        Priority:
                                        <strong>
                                            ${escapeHtml(
                                                report.rescue_priority ||
                                                "--"
                                            )}
                                        </strong>
                                    </p>

                                </div>

                                <span class="badge">
                                    ${escapeHtml(
                                        report.flood_severity ||
                                        "N/A"
                                    )}
                                </span>

                            </div>

                        `;

                    }
                ).join("");

        };


    async function loadRecords(
        targetId
    ) {

        const element =
            document.getElementById(
                targetId
            );


        if (!element) {
            return;
        }


        try {

            const data =
                await fetchJson(
                    "/api/history",
                    {
                        cache:
                            "no-store"
                    }
                );


            window.renderRecords(
                data.history || [],
                targetId
            );


        } catch (error) {

            element.innerHTML = `
                <div class="empty-state">
                    ${escapeHtml(
                        error.message
                    )}
                </div>
            `;

        }

    }


    if (
        document.getElementById(
            "historyList"
        )
    ) {

        loadRecords(
            "historyList"
        );


        document
            .getElementById(
                "refreshHistory"
            )
            ?.addEventListener(
                "click",
                () => {

                    loadRecords(
                        "historyList"
                    );

                }
            );


        document
            .getElementById(
                "clearHistory"
            )
            ?.addEventListener(
                "click",
                async () => {

                    if (
                        !confirm(
                            "Clear all saved analysis history?"
                        )
                    ) {

                        return;

                    }


                    try {

                        await fetchJson(
                            "/api/history",
                            {
                                method:
                                    "DELETE"
                            }
                        );


                        loadRecords(
                            "historyList"
                        );

                    } catch (error) {

                        alert(
                            error.message
                        );

                    }

                }
            );

    }


    if (
        document.getElementById(
            "reportsList"
        )
    ) {

        loadRecords(
            "reportsList"
        );


        document
            .getElementById(
                "refreshReports"
            )
            ?.addEventListener(
                "click",
                () => {

                    loadRecords(
                        "reportsList"
                    );

                }
            );

    }


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


    // ============================================================
    // START
    // ============================================================

    setupTheme();

})();