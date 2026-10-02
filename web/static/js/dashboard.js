(() => {

    "use strict";


    // ============================================================
    // ELEMENTS
    // ============================================================

    const input =
        document.getElementById("imageInput");

    const drop =
        document.getElementById("dropzone");

    const previewSection =
        document.getElementById("previewSection");

    const preview =
        document.getElementById("imagePreview");

    const filename =
        document.getElementById("selectedFilename");

    const analyze =
        document.getElementById("analyzeButton");


    // ============================================================
    // STOP IF THIS PAGE DOES NOT USE THE ANALYSIS UI
    // ============================================================

    if (
        !input ||
        !drop ||
        !previewSection ||
        !preview ||
        !filename ||
        !analyze
    ) {
        return;
    }


    let selectedFile = null;


    // ============================================================
    // FILE SELECTION
    // ============================================================

    drop.addEventListener("click", () => {
        input.click();
    });


    input.addEventListener("change", () => {

        selectedFile =
            input.files[0] || null;


        if (!selectedFile) {
            return;
        }


        preview.src =
            URL.createObjectURL(selectedFile);


        filename.textContent =
            selectedFile.name;


        previewSection.hidden =
            false;

    });


    // ============================================================
    // ANALYZE IMAGE
    // ============================================================

    analyze.addEventListener(
        "click",
        async () => {

            if (!selectedFile) {

                alert(
                    "Select an image first."
                );

                return;
            }


            analyze.disabled =
                true;

            analyze.textContent =
                "ANALYZING...";


            const form =
                new FormData();

            form.append(
                "image",
                selectedFile
            );


            try {

                const response =
                    await fetch(
                        "/analyze",
                        {
                            method: "POST",
                            body: form
                        }
                    );


                const data =
                    await response.json();


                console.log(
                    "DroneRescue AI RESULT:",
                    data
                );


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
                // IMPORTANT
                // Flask returns:
                //
                // {
                //   success: true,
                //   result: {
                //      assessment: {...},
                //      vehicle_breakdown: {...},
                //      segmentation_image: "...",
                //      pipeline: {...}
                //   }
                // }
                // ==================================================

                renderDashboardResult(
                    data.result
                );


                // --------------------------------------------------
                // Save complete result locally
                // --------------------------------------------------

                try {

                    localStorage.setItem(
                        "droneRescueLatest",
                        JSON.stringify(
                            createHistoryRecord(
                                data.result,
                                selectedFile
                            )
                        )
                    );

                } catch (storageError) {

                    console.warn(
                        "Could not save latest analysis:",
                        storageError
                    );

                }


            } catch (error) {

                console.error(
                    "DroneRescue analysis error:",
                    error
                );


                showAnalysisError(
                    error.message ||
                    "Analysis failed."
                );


            } finally {

                analyze.disabled =
                    false;

                analyze.textContent =
                    "ANALYZE IMAGE";

            }

        }
    );


    // ============================================================
    // NORMALIZE BACKEND RESULT
    // ============================================================

    function getReportAndBreakdown(result) {

        // --------------------------------------------------------
        // Current Flask format
        // --------------------------------------------------------

        if (
            result &&
            result.assessment
        ) {

            return {

                report:
                    result.assessment || {},

                breakdown:
                    result.vehicle_breakdown || {},

                segmentationImage:
                    result.segmentation_image || "",

                pipeline:
                    result.pipeline || {}

            };

        }


        // --------------------------------------------------------
        // Backward-compatible format
        // --------------------------------------------------------

        if (
            result &&
            result.report
        ) {

            return {

                report:
                    result.report || {},

                breakdown:
                    result.vehicle_breakdown || {},

                segmentationImage:
                    result.segmentation_image || "",

                pipeline:
                    result.pipeline || {}

            };

        }


        // --------------------------------------------------------
        // Very old direct-report format
        // --------------------------------------------------------

        return {

            report:
                result || {},

            breakdown:
                {},

            segmentationImage:
                "",

            pipeline:
                {}

        };

    }


    // ============================================================
    // RENDER DASHBOARD RESULT
    // ============================================================

    function renderDashboardResult(
        result
    ) {

        const {
            report,
            breakdown,
            segmentationImage,
            pipeline
        } =
            getReportAndBreakdown(
                result
            );


        console.log(
            "DroneRescue assessment:",
            report
        );


        // ========================================================
        // TOP METRICS
        // ========================================================

        const floodStatus =
            document.getElementById(
                "floodStatus"
            );

        const floodProbability =
            document.getElementById(
                "floodProbability"
            );

        const peopleCount =
            document.getElementById(
                "peopleCount"
            );

        const vehicleCount =
            document.getElementById(
                "vehicleCount"
            );


        if (floodStatus) {

            floodStatus.textContent =
                report.flood_detected ??
                "--";

        }


        if (floodProbability) {

            floodProbability.textContent =
                `${Number(
                    report.flood_probability ?? 0
                ).toFixed(2)}%`;

        }


        if (peopleCount) {

            peopleCount.textContent =
                Number(
                    report.people_visible ?? 0
                );

        }


        if (vehicleCount) {

            vehicleCount.textContent =
                Number(
                    report.vehicles_visible ?? 0
                );

        }


        // ========================================================
        // SEGMENTATION IMAGE
        // ========================================================

        const segmentation =
            document.getElementById(
                "segmentationPanel"
            );


        if (segmentation) {

            const imageUrl =
                segmentationImage ||
                report.segmentation_image ||
                "";


            if (imageUrl) {

                segmentation.innerHTML = `

                    <img
                        src="${escapeHtml(imageUrl)}"
                        alt="Full image semantic segmentation overlay"
                        class="segmentation-image"
                    >

                `;

            } else {

                segmentation.innerHTML = `

                    <div class="empty-state">
                        Segmentation image is not available.
                    </div>

                `;

            }

        }


        // ========================================================
        // EMERGENCY ASSESSMENT
        // ========================================================

        const assessment =
            document.getElementById(
                "assessmentPanel"
            );


        if (assessment) {

            assessment.innerHTML =
                formatReport(
                    report
                );

        }


        // ========================================================
        // VEHICLE BREAKDOWN
        // ========================================================

        const vehiclePanel =
            document.getElementById(
                "vehiclePanel"
            );


        if (vehiclePanel) {

            const names = [
                "Bicycle",
                "Car",
                "Motorcycle",
                "Bus",
                "Truck"
            ];


            vehiclePanel.innerHTML =
                names.map(
                    name => `

                        <div class="vehicle-box">

                            <span>
                                ${escapeHtml(name)}
                            </span>

                            <strong>
                                ${Number(
                                    breakdown[name] ?? 0
                                )}
                            </strong>

                        </div>

                    `
                ).join("");

        }


        // ========================================================
        // SUMMARY
        // ========================================================

        const summary =
            document.getElementById(
                "summaryPanel"
            );


        if (summary) {

            const situationSummary =
                report.situation_summary ||
                "The AI pipeline completed the analysis.";

            const recommendedAction =
                report.recommended_action ||
                "Review the analysis results and assess the affected area.";


            summary.innerHTML = `

                <h3>
                    AI Situation Summary
                </h3>

                <p>
                    ${escapeHtml(
                        situationSummary
                    )}
                </p>

                <h3>
                    Recommended Action
                </h3>

                <p>
                    ${escapeHtml(
                        recommendedAction
                    )}
                </p>

                <div class="summary-details">

                    <p>
                        Flood Status:
                        <strong>
                            ${escapeHtml(
                                report.flood_detected ??
                                "--"
                            )}
                        </strong>
                    </p>

                    <p>
                        Flood Probability:
                        <strong>
                            ${Number(
                                report.flood_probability ?? 0
                            ).toFixed(2)}%
                        </strong>
                    </p>

                    <p>
                        Flood Coverage:
                        <strong>
                            ${Number(
                                report.flood_coverage ?? 0
                            ).toFixed(2)}%
                        </strong>
                    </p>

                    <p>
                        Building Impact:
                        <strong>
                            ${Number(
                                report.flooded_building_area ?? 0
                            ).toFixed(2)}%
                        </strong>
                    </p>

                    <p>
                        Road Impact:
                        <strong>
                            ${Number(
                                report.flooded_road_area ?? 0
                            ).toFixed(2)}%
                        </strong>
                    </p>

                    <p>
                        Severity:
                        <strong>
                            ${escapeHtml(
                                report.flood_severity ??
                                "--"
                            )}
                        </strong>
                    </p>

                    <p>
                        Rescue Priority:
                        <strong>
                            ${escapeHtml(
                                report.rescue_priority ??
                                "--"
                            )}
                        </strong>
                    </p>

                    <p>
                        People:
                        <strong>
                            ${Number(
                                report.people_visible ?? 0
                            )}
                        </strong>

                        &nbsp;&nbsp;

                        Vehicles:
                        <strong>
                            ${Number(
                                report.vehicles_visible ?? 0
                            )}
                        </strong>
                    </p>

                </div>

            `;

        }


        // ========================================================
        // PIPELINE STATUS
        // ========================================================

        const pipelineStatus =
            document.getElementById(
                "pipelineStatus"
            );


        if (pipelineStatus) {

            pipelineStatus.textContent =
                pipeline.status ||
                "COMPLETED";

        }


        // ========================================================
        // ANALYSIS RESULT CONTAINER
        // ========================================================

        const resultSection =
            document.getElementById(
                "analysisResult"
            );


        if (resultSection) {

            resultSection.hidden =
                false;

        }

    }


    // ============================================================
    // EMERGENCY REPORT
    // ============================================================

    function formatReport(
        report
    ) {

        return `

            <div class="assessment-grid">

                <div class="assessment-item">

                    <span>
                        FLOOD STATUS
                    </span>

                    <strong>
                        ${escapeHtml(
                            report.flood_detected ??
                            "--"
                        )}
                    </strong>

                </div>


                <div class="assessment-item">

                    <span>
                        FLOOD SEVERITY
                    </span>

                    <strong>
                        ${escapeHtml(
                            report.flood_severity ??
                            "--"
                        )}
                    </strong>

                </div>


                <div class="assessment-item">

                    <span>
                        RESCUE PRIORITY
                    </span>

                    <strong>
                        ${escapeHtml(
                            report.rescue_priority ??
                            "--"
                        )}
                    </strong>

                </div>


                <div class="assessment-item">

                    <span>
                        PEOPLE VISIBLE
                    </span>

                    <strong>
                        ${Number(
                            report.people_visible ?? 0
                        )}
                    </strong>

                </div>


                <div class="assessment-item">

                    <span>
                        VEHICLES VISIBLE
                    </span>

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

    }


    // ============================================================
    // CREATE LOCAL HISTORY RECORD
    // ============================================================

    function createHistoryRecord(
        result,
        file
    ) {

        const {
            report,
            breakdown,
            segmentationImage,
            pipeline
        } =
            getReportAndBreakdown(
                result
            );


        return {

            filename:
                file
                    ? file.name
                    : "Analyzed image",

            image_url:
                preview
                    ? preview.src
                    : "",

            report:
                report,

            vehicle_breakdown:
                breakdown,

            segmentation_image:
                segmentationImage,

            pipeline:
                pipeline,

            analyzed_at:
                new Date().toISOString()

        };

    }


    // ============================================================
    // LOAD LATEST ANALYSIS
    // ============================================================

    async function loadLatestAnalysis() {

        // --------------------------------------------------------
        // First try backend history
        // --------------------------------------------------------

        try {

            const response =
                await fetch(
                    "/api/latest",
                    {
                        method: "GET",
                        cache: "no-store"
                    }
                );


            if (response.ok) {

                const data =
                    await response.json();


                if (
                    data.success &&
                    data.record
                ) {

                    restoreRecord(
                        data.record
                    );

                    return;

                }

            }

        } catch (error) {

            console.warn(
                "Backend latest analysis unavailable:",
                error
            );

        }


        // --------------------------------------------------------
        // Browser localStorage fallback
        // --------------------------------------------------------

        try {

            const local =
                localStorage.getItem(
                    "droneRescueLatest"
                );


            if (!local) {
                return;
            }


            const record =
                JSON.parse(
                    local
                );


            if (record) {

                restoreRecord(
                    record
                );

            }

        } catch (error) {

            console.warn(
                "Local result restore failed:",
                error
            );

        }

    }


    // ============================================================
    // RESTORE SAVED RECORD
    // ============================================================

    function restoreRecord(
        record
    ) {

        if (!record) {
            return;
        }


        const report =
            record.report ||
            record.assessment ||
            {};


        const result = {

            assessment:
                report,

            vehicle_breakdown:
                record.vehicle_breakdown ||
                {},

            segmentation_image:
                record.segmentation_image ||
                "",

            pipeline:
                record.pipeline ||
                {}

        };


        // --------------------------------------------------------
        // Restore uploaded image
        // --------------------------------------------------------

        if (
            record.image_url &&
            preview &&
            filename &&
            previewSection
        ) {

            preview.src =
                record.image_url;


            filename.textContent =
                record.filename ||
                "Latest analyzed image";


            previewSection.hidden =
                false;

        }


        // --------------------------------------------------------
        // Restore complete dashboard
        // --------------------------------------------------------

        renderDashboardResult(
            result
        );

    }


    // ============================================================
    // ERROR DISPLAY
    // ============================================================

    function showAnalysisError(
        message
    ) {

        const errorBox =
            document.getElementById(
                "analysisError"
            );


        if (errorBox) {

            errorBox.textContent =
                message;

            errorBox.hidden =
                false;

            return;

        }


        alert(message);

    }


    // ============================================================
    // ESCAPE HTML
    // ============================================================

    function escapeHtml(
        value
    ) {

        return String(
            value
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
    // LOAD
    // ============================================================

    loadLatestAnalysis();


})();