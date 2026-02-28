/** @odoo-module **/

import { Component, useState, onMounted, onWillUnmount } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

/**
 * Garment Barcode/QR Scanner — OWL Component
 *
 * Camera-based barcode & QR code scanner for inventory counting.
 * Uses BarcodeDetector API (Chrome/Edge 83+) with getUserMedia.
 * Falls back to manual input when camera is unavailable.
 */
export class GarmentBarcodeScanner extends Component {
    static template = "garment_inventory.BarcodeScanner";

    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
        this.notification = useService("notification");

        const params = this.props.action?.params || {};
        this.inventoryId = params.inventory_id || false;
        this.inventoryName = params.inventory_name || "";

        this.state = useState({
            // Camera state
            cameraActive: false,
            cameraError: "",
            hasBarcodeDetector: false,
            // Scan state
            lastScanned: "",
            scanCount: 0,
            scanHistory: [],
            processing: false,
            // Manual input
            manualCode: "",
            manualQty: 1,
            // Feedback
            feedback: "",
            feedbackType: "", // success, error, warning
        });

        this._stream = null;
        this._videoEl = null;
        this._canvasEl = null;
        this._detector = null;
        this._animFrame = null;
        this._scanCooldown = false;

        onMounted(() => {
            this._checkCapabilities();
        });

        onWillUnmount(() => {
            this._stopCamera();
        });
    }

    // =====================================================================
    // Camera capabilities check
    // =====================================================================
    _checkCapabilities() {
        this.state.hasBarcodeDetector =
            typeof window.BarcodeDetector !== "undefined";
    }

    // =====================================================================
    // Camera lifecycle
    // =====================================================================
    async startCamera() {
        this.state.cameraError = "";
        this.state.feedback = "";

        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
            this.state.cameraError =
                "Trình duyệt không hỗ trợ camera. Vui lòng dùng Chrome/Edge.";
            return;
        }
        if (!this.state.hasBarcodeDetector) {
            this.state.cameraError =
                "Trình duyệt không hỗ trợ BarcodeDetector. Vui lòng dùng Chrome/Edge phiên bản mới nhất, hoặc nhập mã thủ công bên dưới.";
            return;
        }

        try {
            this._detector = new window.BarcodeDetector({
                formats: [
                    "qr_code",
                    "ean_13",
                    "ean_8",
                    "code_128",
                    "code_39",
                    "code_93",
                    "upc_a",
                    "upc_e",
                    "itf",
                    "data_matrix",
                ],
            });
        } catch {
            this.state.cameraError =
                "Không thể khởi tạo BarcodeDetector.";
            return;
        }

        try {
            this._stream = await navigator.mediaDevices.getUserMedia({
                video: {
                    facingMode: { ideal: "environment" },
                    width: { ideal: 1280 },
                    height: { ideal: 720 },
                },
                audio: false,
            });
        } catch (err) {
            if (err.name === "NotAllowedError") {
                this.state.cameraError =
                    "Bạn chưa cấp quyền camera. Vui lòng cho phép truy cập camera trong trình duyệt.";
            } else if (err.name === "NotFoundError") {
                this.state.cameraError =
                    "Không tìm thấy camera trên thiết bị này.";
            } else {
                this.state.cameraError =
                    "Lỗi mở camera: " + (err.message || err.name);
            }
            return;
        }

        this._videoEl = document.getElementById("garment-scanner-video");
        this._canvasEl = document.getElementById("garment-scanner-canvas");

        if (!this._videoEl || !this._canvasEl) {
            this.state.cameraError = "Không tìm thấy phần tử video.";
            this._stopCamera();
            return;
        }

        this._videoEl.srcObject = this._stream;
        await this._videoEl.play();
        this.state.cameraActive = true;

        this._scanLoop();
    }

    _stopCamera() {
        if (this._animFrame) {
            cancelAnimationFrame(this._animFrame);
            this._animFrame = null;
        }
        if (this._stream) {
            this._stream.getTracks().forEach((t) => t.stop());
            this._stream = null;
        }
        if (this._videoEl) {
            this._videoEl.srcObject = null;
        }
        this.state.cameraActive = false;
    }

    stopCamera() {
        this._stopCamera();
    }

    // =====================================================================
    // Barcode detection loop
    // =====================================================================
    async _scanLoop() {
        if (!this.state.cameraActive || !this._videoEl || !this._detector) {
            return;
        }

        if (
            this._videoEl.readyState >= 2 &&
            !this._scanCooldown &&
            !this.state.processing
        ) {
            try {
                const barcodes = await this._detector.detect(this._videoEl);
                if (barcodes.length > 0) {
                    const code = barcodes[0].rawValue;
                    if (code && code !== this.state.lastScanned) {
                        await this._onBarcodeDetected(code);
                    }
                }
            } catch {
                // Detection can fail on some frames — continue
            }
        }

        this._animFrame = requestAnimationFrame(() => this._scanLoop());
    }

    async _onBarcodeDetected(code) {
        // Cooldown to avoid rapid re-scans of same code
        this._scanCooldown = true;
        this.state.lastScanned = code;

        // Beep feedback
        this._playBeep();

        await this._processBarcode(code, 1);

        // 1.5s cooldown before allowing same code again
        setTimeout(() => {
            this._scanCooldown = false;
            this.state.lastScanned = "";
        }, 1500);
    }

    // =====================================================================
    // Barcode processing (RPC to backend)
    // =====================================================================
    async _processBarcode(code, qty) {
        if (!this.inventoryId) {
            this._showFeedback("Không có phiếu kiểm kê!", "error");
            return;
        }

        this.state.processing = true;
        try {
            const result = await this.orm.call(
                "garment.inventory",
                "process_barcode_scan",
                [[this.inventoryId], code, qty],
            );

            if (result.success) {
                this.state.scanCount++;
                this.state.scanHistory.unshift({
                    code: code,
                    qty: qty,
                    item_name: result.item_name || code,
                    time: new Date().toLocaleTimeString("vi-VN"),
                    is_new: result.is_new,
                });
                // Keep only last 20 entries
                if (this.state.scanHistory.length > 20) {
                    this.state.scanHistory.pop();
                }
                this._showFeedback(
                    `✅ ${result.item_name || code} — SL: ${result.total_qty}`,
                    "success",
                );
            } else {
                this._showFeedback(
                    result.message || "Lỗi xử lý mã",
                    "error",
                );
            }
        } catch (err) {
            this._showFeedback("Lỗi kết nối: " + (err.message || ""), "error");
        }
        this.state.processing = false;
    }

    // =====================================================================
    // Manual input
    // =====================================================================
    onManualCodeInput(ev) {
        this.state.manualCode = ev.target.value;
    }

    onManualQtyInput(ev) {
        this.state.manualQty = parseFloat(ev.target.value) || 1;
    }

    async onManualScan() {
        const code = (this.state.manualCode || "").trim();
        if (!code) {
            this._showFeedback("Vui lòng nhập mã barcode/QR!", "warning");
            return;
        }
        await this._processBarcode(code, this.state.manualQty);
        this.state.manualCode = "";
        // Re-focus the input
        const input = document.getElementById("garment-manual-barcode-input");
        if (input) {
            input.focus();
        }
    }

    onManualKeydown(ev) {
        if (ev.key === "Enter") {
            this.onManualScan();
        }
    }

    // =====================================================================
    // Navigation
    // =====================================================================
    goBack() {
        this._stopCamera();
        if (this.inventoryId) {
            this.action.doAction({
                type: "ir.actions.act_window",
                res_model: "garment.inventory",
                res_id: this.inventoryId,
                views: [[false, "form"]],
                target: "current",
            });
        } else {
            this.action.doAction({
                type: "ir.actions.act_window",
                res_model: "garment.inventory",
                views: [[false, "list"]],
                target: "current",
            });
        }
    }

    // =====================================================================
    // Feedback helpers
    // =====================================================================
    _showFeedback(msg, type) {
        this.state.feedback = msg;
        this.state.feedbackType = type;
        // Auto-clear after 3s
        clearTimeout(this._feedbackTimer);
        this._feedbackTimer = setTimeout(() => {
            this.state.feedback = "";
            this.state.feedbackType = "";
        }, 3000);
    }

    _playBeep() {
        try {
            const ctx = new (window.AudioContext || window.webkitAudioContext)();
            const osc = ctx.createOscillator();
            const gain = ctx.createGain();
            osc.connect(gain);
            gain.connect(ctx.destination);
            osc.frequency.value = 1200;
            osc.type = "sine";
            gain.gain.value = 0.3;
            osc.start();
            osc.stop(ctx.currentTime + 0.15);
        } catch {
            // Audio not available — skip silently
        }
    }
}

registry
    .category("actions")
    .add("garment_barcode_scanner", GarmentBarcodeScanner);
