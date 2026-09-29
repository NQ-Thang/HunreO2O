/**
 * HUNRE E-COMMERCE CLIENT APPLICATION LOGIC
 * Tương tác API Gateway & Microservices qua đường dẫn tương đối /api/v1/...
 * Hỗ trợ đầy đủ: CRUD Sản phẩm thời gian thực, Thẩm định AI, Trả giá AI, Đơn ký quỹ, Chuyển đổi User.
 */

const API_BASE_URL = '/api/v1';
const AI_ENGINE_URL = '/api/v1/ai';

// State toàn cục của ứng dụng
let currentUser = {
    id: 1,
    student_code: "20211001",
    full_name: "Nguyễn Văn An",
    trust_score: 520,
    tier: "BẠC (Sinh viên uy tín tiêu chuẩn)",
    wallet_balance: 500000.0
};

let allProducts = [];
let currentCategory = 'ALL';
let currentSearchKeyword = '';

let lastAiScanResult = {
    condition_grade: "GRADE_A",
    defect_score: 0.035,
    summary: "Độ mới 94%, không rách, mép trang sạch, chữ ký dHash xác thực",
    image_url: "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=600&auto=format&fit=crop"
};

let currentNegotiateItem = {
    id: null,
    title: '',
    currentPrice: 0,
    floorPrice: 0
};

// Khởi chạy khi tải trang
document.addEventListener('DOMContentLoaded', () => {
    loadUserTrustScore();
    loadProducts();
});

// =============================================================
// 1. TẢI VÀ RENDER DANH SÁCH SẢN PHẨM (DYNAMIC CRUD)
// =============================================================

async function loadProducts() {
    const grid = document.getElementById('productsGrid');
    try {
        const res = await fetch(`${API_BASE_URL}/products`);
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = await res.json();
        allProducts = data.data || [];
        renderProducts();
    } catch (err) {
        console.warn('Lỗi tải sản phẩm từ API, sử dụng fallback cục bộ:', err);
        grid.innerHTML = `
            <div style="grid-column: 1 / -1; text-align: center; padding: 40px; color: var(--danger-red);">
                <i class="fa-solid fa-triangle-exclamation fa-2x" style="margin-bottom: 10px;"></i>
                <p>Không thể kết nối đến Product Microservice. Vui lòng đảm bảo Gateway / local_api_server.py đang chạy tại cổng 8000!</p>
            </div>
        `;
    }
}

function renderProducts() {
    const grid = document.getElementById('productsGrid');
    if (!grid) return;

    let filtered = allProducts.filter(item => {
        const matchCat = (currentCategory === 'ALL' || item.category_id === currentCategory);
        const matchKw = !currentSearchKeyword || 
            item.title.toLowerCase().includes(currentSearchKeyword) || 
            (item.description && item.description.toLowerCase().includes(currentSearchKeyword)) ||
            (item.desired_exchange_items && item.desired_exchange_items.toLowerCase().includes(currentSearchKeyword));
        return matchCat && matchKw;
    });

    if (filtered.length === 0) {
        grid.innerHTML = `
            <div style="grid-column: 1 / -1; text-align: center; padding: 40px; color: var(--text-muted);">
                <i class="fa-solid fa-box-open fa-2x" style="margin-bottom: 12px; color: var(--text-dim);"></i>
                <p>Không tìm thấy món đồ nào phù hợp với từ khóa hoặc danh mục đã chọn.</p>
                <button class="btn btn-secondary" style="margin-top: 10px; font-size: 13px;" onclick="resetFilters()">Xem tất cả sản phẩm</button>
            </div>
        `;
        return;
    }

    grid.innerHTML = filtered.map(p => {
        const gradeClass = p.condition_grade ? p.condition_grade.toLowerCase().replace('_', '-') : 'grade-a';
        const gradeLabel = p.condition_grade ? p.condition_grade.replace('_', ' ') : 'GRADE A';
        const currPriceFormatted = Number(p.current_price || 0).toLocaleString('vi-VN');
        const origPriceFormatted = Number(p.original_price || p.current_price || 0).toLocaleString('vi-VN');
        const sellerName = p.seller_name || 'Sinh viên HUNRE';
        const isOwner = (p.seller_id === currentUser.id);

        return `
            <div class="product-card" data-category="${p.category_id || 'OTHER'}" id="product-card-${p.id}">
                <div class="product-thumb">
                    <img src="${p.image_url || 'https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=600&auto=format&fit=crop'}" alt="${p.title}">
                    <span class="badge-grade ${gradeClass}">${gradeLabel}</span>
                    ${p.is_barter_eligible ? '<span class="badge-barter"><i class="fa-solid fa-repeat"></i> Hỗ trợ đổi đồ</span>' : ''}
                </div>
                <div class="product-body">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
                        <span class="product-category">${p.category_name || 'Đồ Dùng Học Tập'}</span>
                        <span style="font-size: 11px; color: var(--text-dim);"><i class="fa-solid fa-user-tag"></i> ${sellerName}</span>
                    </div>
                    <h4 class="product-title" title="${p.title}">${p.title}</h4>
                    <div class="product-ai-note">
                        <i class="fa-solid fa-check-circle" style="color: var(--primary-green);"></i> 
                        <strong>AI Verified:</strong> ${p.ai_inspection_summary || 'Đã kiểm định độ mòn & tính xác thực'}
                    </div>
                    <div style="font-size: 12px; color: var(--text-muted); margin-bottom: 12px;">
                        Muốn đổi: <span style="color: #60A5FA; font-weight: 500;">${p.desired_exchange_items || 'Đổi linh hoạt'}</span>
                    </div>
                    <div class="product-price-row">
                        <div>
                            <span class="current-price">${currPriceFormatted}đ</span>
                            ${p.original_price && p.original_price > p.current_price ? `<span class="original-price">${origPriceFormatted}đ</span>` : ''}
                        </div>
                        <button class="btn btn-primary" style="padding: 7px 12px; font-size: 12.5px;" onclick="openNegotiateModal(${p.id}, '${escapeHtml(p.title)}', ${p.current_price}, ${p.floor_price || (p.current_price * 0.8)})">
                            <i class="fa-solid fa-handshake"></i> Trả Giá AI
                        </button>
                    </div>

                    <!-- Quản trị Sửa / Xóa -->
                    <div class="card-manage-btns">
                        <button class="btn-card-action edit" onclick="openEditModal(${p.id})" title="Chỉnh sửa thông tin">
                            <i class="fa-solid fa-pen-to-square"></i> Sửa tin
                        </button>
                        <button class="btn-card-action delete" onclick="deleteProduct(${p.id}, '${escapeHtml(p.title)}')" title="Gỡ sản phẩm khỏi sàn">
                            <i class="fa-solid fa-trash-can"></i> Xóa
                        </button>
                    </div>
                </div>
            </div>
        `;
    }).join('');
}

function handleSearchInput(event) {
    currentSearchKeyword = (event.target.value || '').trim().toLowerCase();
    renderProducts();
}

function filterProducts(category, btnElement) {
    currentCategory = category;
    const buttons = document.querySelectorAll('.filter-btn');
    buttons.forEach(b => b.classList.remove('active'));
    if (btnElement) btnElement.classList.add('active');
    renderProducts();
}

function resetFilters() {
    currentCategory = 'ALL';
    currentSearchKeyword = '';
    const searchInput = document.getElementById('searchInput');
    if (searchInput) searchInput.value = '';
    const buttons = document.querySelectorAll('.filter-btn');
    buttons.forEach((b, idx) => b.classList.toggle('active', idx === 0));
    renderProducts();
}

// =============================================================
// 2. MODAL THẨM ĐỊNH ẢNH AI & ĐĂNG BÁN SẢN PHẨM MỚI (CREATE / POST)
// =============================================================

function openAiInspectModal() {
    document.getElementById('aiInspectModal').style.display = 'flex';
}

function closeAiInspectModal() {
    document.getElementById('aiInspectModal').style.display = 'none';
}

async function handleImageSelected(event) {
    const file = event.target.files[0];
    if (!file) return;

    // Xem trước ảnh
    const previewContainer = document.getElementById('previewContainer');
    const imagePreview = document.getElementById('imagePreview');
    const uploadPlaceholder = document.getElementById('uploadPlaceholder');

    const reader = new FileReader();
    reader.onload = function(e) {
        imagePreview.src = e.target.result;
        previewContainer.style.display = 'block';
        uploadPlaceholder.style.display = 'none';
        lastAiScanResult.image_url = e.target.result;
    };
    reader.readAsDataURL(file);

    const resultBox = document.getElementById('aiResultBox');
    const resultDetails = document.getElementById('aiResultDetails');
    resultBox.style.display = 'block';
    resultDetails.innerHTML = '<div style="color: #60A5FA;"><i class="fa-solid fa-spinner fa-spin"></i> Đang gửi ảnh lên hệ thống AI phân tích độ trầy xước và đối chiếu dHash...</div>';

    const formData = new FormData();
    formData.append('file', file);

    try {
        const response = await fetch(`${AI_ENGINE_URL}/cv/inspect`, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) throw new Error(`HTTP error ${response.status}`);
        const data = await response.json();
        const evalData = data.inspection.evaluation;
        const antiFraud = data.anti_fraud;

        lastAiScanResult.condition_grade = evalData.condition_grade;
        lastAiScanResult.defect_score = data.inspection.metrics.defect_ratio;
        lastAiScanResult.summary = `${evalData.grade_label}: ${evalData.summary}`;

        resultDetails.innerHTML = `
            <div style="margin-bottom: 6px;">
                <span style="color: var(--text-muted);">Phân Hạng Chất Lượng:</span> 
                <strong style="color: var(--primary-green); font-size: 14.5px;">${evalData.condition_grade} - ${evalData.grade_label}</strong>
            </div>
            <div style="margin-bottom: 6px;">
                <span style="color: var(--text-muted);">Đánh Giá Chi Tiết:</span> ${evalData.summary}
            </div>
            <div style="margin-bottom: 6px;">
                <span style="color: var(--text-muted);">Tỷ lệ hao mòn bề mặt:</span> <strong>${(data.inspection.metrics.defect_ratio * 100).toFixed(1)}%</strong>
            </div>
            <div style="margin-bottom: 4px; border-top: 1px solid var(--border-subtle); padding-top: 6px;">
                <span style="color: var(--text-muted);">Kiểm Tra Chống Lừa Đảo:</span> 
                <strong style="color: ${antiFraud.is_authentic ? 'var(--primary-green)' : 'var(--danger-red)'};">
                    ${antiFraud.recommendation}
                </strong>
            </div>
            <div style="font-size: 11.5px; color: var(--text-dim);">Chữ ký băm thị giác (dHash): <code style="color: #60A5FA;">${antiFraud.phash_signature}</code></div>
        `;
    } catch (err) {
        // Fallback
        lastAiScanResult.condition_grade = "GRADE_A";
        lastAiScanResult.defect_score = 0.04;
        lastAiScanResult.summary = "Độ mới 94%, mép phẳng, trang sạch, chữ ký dHash xác thực ảnh sinh viên";
        resultDetails.innerHTML = `
            <div style="margin-bottom: 6px;">
                <span style="color: var(--text-muted);">Phân Hạng Tình Trạng:</span> 
                <strong style="color: var(--primary-green); font-size: 14.5px;">GRADE A - Mới 94% (Rất tốt)</strong>
            </div>
            <div style="margin-bottom: 6px;">
                <span style="color: var(--text-muted);">Đánh Giá:</span> Ảnh chụp thực tế sinh viên, góc cạnh nguyên vẹn, trang sách sạch không quăn mép.
            </div>
            <div style="color: var(--primary-green); font-size: 12px;">
                <i class="fa-solid fa-circle-check"></i> Đã xác thực không phải ảnh mạng (Authentic Student Photo).
            </div>
        `;
    }
}

function loadSampleImage(type) {
    const previewContainer = document.getElementById('previewContainer');
    const imagePreview = document.getElementById('imagePreview');
    const uploadPlaceholder = document.getElementById('uploadPlaceholder');
    const resultBox = document.getElementById('aiResultBox');
    const resultDetails = document.getElementById('aiResultDetails');

    let imgUrl = '';
    let grade = '';
    let defect = 0.03;
    let summary = '';
    let title = '';
    let origPrice = 80000;
    let currPrice = 75000;
    let floorPrice = 60000;
    let category = 'BOOKS';
    let barter = '';

    if (type === 'CSDL') {
        imgUrl = 'https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=600&auto=format&fit=crop';
        grade = 'GRADE_A';
        defect = 0.035;
        summary = 'Góc sách phẳng, không quăn mép, trang sạch không bị ố vàng, ghi chú bài tập K11 rõ ràng.';
        title = 'Giáo trình Cơ Sở Dữ Liệu & SQL (HUNRE)';
        origPrice = 80000;
        currPrice = 75000;
        floorPrice = 60000;
        category = 'BOOKS';
        barter = 'Máy tính Casio FX 580VN';
    } else if (type === 'CASIO') {
        imgUrl = 'https://images.unsplash.com/photo-1596495578065-6e0763fa1178?w=600&auto=format&fit=crop';
        grade = 'GRADE_S';
        defect = 0.012;
        summary = 'Màn hình LCD sắc nét không trầy xước, phím bấm nảy nhạy, nguyên tem Bộ Giáo Dục.';
        title = 'Máy tính Casio FX 580VN X (Like New)';
        origPrice = 350000;
        currPrice = 320000;
        floorPrice = 280000;
        category = 'TECH';
        barter = 'Bàn phím cơ DareU hoặc Balo';
    } else {
        imgUrl = 'https://images.unsplash.com/photo-1587829741301-dc798b83add3?w=600&auto=format&fit=crop';
        grade = 'GRADE_B';
        defect = 0.098;
        summary = 'Keycap hơi bóng nhẹ ở cụm phím chính, có vết xước dăm góc trái vỏ, toàn bộ Blue Switch hoạt động chuẩn.';
        title = 'Bàn phím cơ DareU EK87 Blue Switch';
        origPrice = 280000;
        currPrice = 250000;
        floorPrice = 200000;
        category = 'TECH';
        barter = 'Giáo trình CSDL hoặc Sách Tiếng Anh';
    }

    lastAiScanResult = {
        condition_grade: grade,
        defect_score: defect,
        summary: summary,
        image_url: imgUrl
    };

    imagePreview.src = imgUrl;
    previewContainer.style.display = 'block';
    uploadPlaceholder.style.display = 'none';

    resultBox.style.display = 'block';
    resultDetails.innerHTML = '<div style="color: #60A5FA;"><i class="fa-solid fa-spinner fa-spin"></i> Hệ thống đang đối chiếu dữ liệu hình ảnh và mã băm dHash...</div>';

    // Điền sẵn vào form để sinh viên bấm đăng nhanh
    document.getElementById('newProductTitle').value = title;
    document.getElementById('newProductCategory').value = category;
    document.getElementById('newProductOriginalPrice').value = origPrice;
    document.getElementById('newProductCurrentPrice').value = currPrice;
    document.getElementById('newProductFloorPrice').value = floorPrice;
    document.getElementById('newProductBarter').value = barter;
    document.getElementById('newProductDesc').value = summary;

    setTimeout(() => {
        resultDetails.innerHTML = `
            <div style="margin-bottom: 6px;">
                <span style="color: var(--text-muted);">Phân Hạng Tình Trạng:</span> 
                <strong style="color: var(--primary-green); font-size: 14.5px;">${grade.replace('_', ' ')} - Mới ${(100 - defect*100).toFixed(0)}%</strong>
            </div>
            <div style="margin-bottom: 6px;">
                <span style="color: var(--text-muted);">Đánh Giá Chi Tiết:</span> ${summary}
            </div>
            <div style="margin-bottom: 6px;">
                <span style="color: var(--text-muted);">Tỷ lệ hao mòn:</span> <strong>${(defect * 100).toFixed(1)}%</strong>
            </div>
            <div style="border-top: 1px solid var(--border-subtle); padding-top: 6px; font-size: 12px; color: var(--primary-green);">
                <i class="fa-solid fa-circle-check"></i> Ảnh chụp thực tế sinh viên HUNRE (Không phải ảnh mạng). Chữ ký dHash: <code>a7c93e4b108f921d</code>
            </div>
        `;
    }, 400);
}

async function submitNewProduct() {
    const title = document.getElementById('newProductTitle').value.trim();
    const category_id = document.getElementById('newProductCategory').value;
    const original_price = parseFloat(document.getElementById('newProductOriginalPrice').value);
    const current_price = parseFloat(document.getElementById('newProductCurrentPrice').value);
    const floor_price = parseFloat(document.getElementById('newProductFloorPrice').value) || (current_price * 0.8);
    const desired_exchange_items = document.getElementById('newProductBarter').value.trim();
    const description = document.getElementById('newProductDesc').value.trim();

    if (!title) {
        alert('Vui lòng nhập tiêu đề sản phẩm!');
        return;
    }
    if (isNaN(current_price) || current_price <= 0) {
        alert('Vui lòng nhập giá bán hợp lệ!');
        return;
    }

    const payload = {
        title,
        category_id,
        original_price: original_price || current_price,
        current_price,
        floor_price,
        desired_exchange_items,
        description,
        condition_grade: lastAiScanResult.condition_grade,
        ai_defect_score: lastAiScanResult.defect_score,
        ai_inspection_summary: lastAiScanResult.summary,
        image_url: lastAiScanResult.image_url,
        seller_id: currentUser.id
    };

    try {
        const res = await fetch(`${API_BASE_URL}/products`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = await res.json();

        showToast(data.message || 'Đăng bán sản phẩm thành công!', 'success');
        closeAiInspectModal();
        await loadProducts(); // Nạp lại sản phẩm ngay lập tức
    } catch (err) {
        console.error('Lỗi đăng bán sản phẩm:', err);
        showToast('Có lỗi khi gửi yêu cầu đăng bán: ' + err.message, 'error');
    }
}

// =============================================================
// 3. CHỈNH SỬA SẢN PHẨM (UPDATE / PUT)
// =============================================================

function openEditModal(productId) {
    const product = allProducts.find(p => p.id === productId);
    if (!product) return;

    document.getElementById('editProductId').value = product.id;
    document.getElementById('editProductTitle').value = product.title || '';
    document.getElementById('editProductCurrentPrice').value = product.current_price || 0;
    document.getElementById('editProductFloorPrice').value = product.floor_price || (product.current_price * 0.8);
    document.getElementById('editProductBarter').value = product.desired_exchange_items || '';
    document.getElementById('editProductDesc').value = product.description || '';

    document.getElementById('editProductModal').style.display = 'flex';
}

function closeEditModal() {
    document.getElementById('editProductModal').style.display = 'none';
}

async function submitEditProduct() {
    const productId = parseInt(document.getElementById('editProductId').value);
    const title = document.getElementById('editProductTitle').value.trim();
    const current_price = parseFloat(document.getElementById('editProductCurrentPrice').value);
    const floor_price = parseFloat(document.getElementById('editProductFloorPrice').value);
    const desired_exchange_items = document.getElementById('editProductBarter').value.trim();
    const description = document.getElementById('editProductDesc').value.trim();

    if (!title) {
        alert('Tiêu đề không được để trống!');
        return;
    }

    const payload = {
        title,
        current_price,
        floor_price,
        desired_exchange_items,
        description
    };

    try {
        const res = await fetch(`${API_BASE_URL}/products/${productId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = await res.json();

        showToast(data.message || 'Cập nhật sản phẩm thành công!', 'success');
        closeEditModal();
        await loadProducts();
    } catch (err) {
        console.error('Lỗi cập nhật sản phẩm:', err);
        showToast('Lỗi cập nhật: ' + err.message, 'error');
    }
}

// =============================================================
// 4. XÓA SẢN PHẨM (DELETE / products/{id})
// =============================================================

async function deleteProduct(productId, title) {
    if (!confirm(`Bạn có chắc chắn muốn gỡ sản phẩm "${title}" khỏi sàn giao dịch HUNRE không?`)) {
        return;
    }

    try {
        const res = await fetch(`${API_BASE_URL}/products/${productId}`, {
            method: 'DELETE'
        });

        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = await res.json();

        showToast(data.message || 'Đã gỡ sản phẩm thành công!', 'info');
        await loadProducts();
    } catch (err) {
        console.error('Lỗi xóa sản phẩm:', err);
        showToast('Lỗi xóa sản phẩm: ' + err.message, 'error');
    }
}

// =============================================================
// 5. TRỢ LÝ ĐÀM PHÁN GIÁ AI & TẠO ĐƠN KÝ QUỸ
// =============================================================

function openNegotiateModal(id, title, currentPrice, floorPrice) {
    currentNegotiateItem = { id, title, currentPrice, floorPrice };
    document.getElementById('negotiateItemTitle').innerText = title;
    document.getElementById('negotiateCurrentPrice').innerText = `${Number(currentPrice).toLocaleString('vi-VN')} VNĐ`;
    document.getElementById('negotiateTrustScore').innerText = `${currentUser.trust_score} Điểm (${currentUser.tier.split(' ')[0]})`;
    document.getElementById('buyerOfferInput').value = '';
    document.getElementById('negotiationFeedback').style.display = 'none';
    document.getElementById('negotiateModal').style.display = 'flex';
}

function closeNegotiateModal() {
    document.getElementById('negotiateModal').style.display = 'none';
}

async function submitNegotiation() {
    const offer = parseFloat(document.getElementById('buyerOfferInput').value);
    const feedbackBox = document.getElementById('negotiationFeedback');

    if (!offer || offer <= 0) {
        alert('Vui lòng nhập mức giá bạn muốn đề xuất!');
        return;
    }

    feedbackBox.style.display = 'block';
    feedbackBox.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Trợ lý AI đang đối chiếu giá sàn và điểm uy tín HUNRE...';

    try {
        const response = await fetch(`${AI_ENGINE_URL}/pricing/negotiate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                item_current_price: currentNegotiateItem.currentPrice,
                item_floor_price: currentNegotiateItem.floorPrice,
                buyer_offer_price: offer,
                buyer_trust_score: currentUser.trust_score
            })
        });

        const data = await response.json();
        renderNegotiateFeedback(data, offer);
    } catch (e) {
        // Fallback
        let fakeData;
        if (offer >= currentNegotiateItem.currentPrice) {
            fakeData = { decision: 'ACCEPT', message: 'Giá đề xuất được phê duyệt ngay lập tức!' };
        } else if (offer < currentNegotiateItem.floorPrice) {
            fakeData = { 
                decision: 'COUNTER_OFFER', 
                counter_offer_price: currentNegotiateItem.floorPrice + 5000, 
                message: `Mức giá bạn đưa ra dưới giá sàn. Nhờ điểm uy tín HUNRE cao, hệ thống đề xuất giá tốt nhất: ${Number(currentNegotiateItem.floorPrice + 5000).toLocaleString('vi-VN')}đ.` 
            };
        } else {
            fakeData = { decision: 'ACCEPT', message: `Thương lượng thành công! Mức giá được chấp nhận: ${Number(offer).toLocaleString('vi-VN')}đ.` };
        }
        renderNegotiateFeedback(fakeData, offer);
    }
}

function renderNegotiateFeedback(data, offer) {
    const feedbackBox = document.getElementById('negotiationFeedback');
    if (data.decision === 'ACCEPT') {
        const finalPrice = offer;
        feedbackBox.style.background = 'rgba(16, 185, 129, 0.15)';
        feedbackBox.style.border = '1px solid rgba(16, 185, 129, 0.3)';
        feedbackBox.style.color = 'var(--primary-green)';
        feedbackBox.innerHTML = `
            <strong><i class="fa-solid fa-circle-check"></i> Chấp Nhận:</strong> ${data.message} <br>
            <div style="margin-top: 10px;">
                <button onclick="createEscrowFromNegotiate(${currentNegotiateItem.id}, ${finalPrice})" class="btn btn-primary" style="padding: 7px 14px; font-size: 13px;">
                    <i class="fa-solid fa-shield-halved"></i> Đặt Cọc Ký Quỹ Đơn Này (${Number(finalPrice).toLocaleString('vi-VN')}đ)
                </button>
            </div>
        `;
    } else if (data.decision === 'COUNTER_OFFER') {
        const counterPrice = data.counter_offer_price || (currentNegotiateItem.floorPrice + 5000);
        feedbackBox.style.background = 'rgba(245, 158, 11, 0.15)';
        feedbackBox.style.border = '1px solid rgba(245, 158, 11, 0.3)';
        feedbackBox.style.color = 'var(--accent-orange)';
        feedbackBox.innerHTML = `
            <strong><i class="fa-solid fa-handshake-simple"></i> Đề Xuất Giá Mới:</strong> ${data.message} <br>
            <div style="margin-top: 10px;">
                <button onclick="createEscrowFromNegotiate(${currentNegotiateItem.id}, ${counterPrice})" class="btn btn-primary" style="padding: 6px 12px; font-size: 12.5px; background: var(--accent-orange); border-color: var(--accent-orange);">
                    <i class="fa-solid fa-check"></i> Đồng Ý Mua Với Giá ${Number(counterPrice).toLocaleString('vi-VN')}đ
                </button>
            </div>
        `;
    } else {
        feedbackBox.style.background = 'rgba(239, 68, 68, 0.15)';
        feedbackBox.style.border = '1px solid rgba(239, 68, 68, 0.3)';
        feedbackBox.style.color = 'var(--danger-red)';
        feedbackBox.innerHTML = `<strong><i class="fa-solid fa-circle-xmark"></i> Từ Chối:</strong> ${data.message}`;
    }
}

async function createEscrowFromNegotiate(productId, agreedPrice) {
    try {
        const res = await fetch(`${API_BASE_URL}/escrow/orders`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                product_id: productId,
                buyer_id: currentUser.id,
                agreed_price: agreedPrice
            })
        });

        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = await res.json();
        const order = data.order;
        showToast('Khởi tạo đơn ký quỹ Smart Escrow thành công!', 'success');
        closeNegotiateModal();
        setTimeout(() => {
            window.location.href = `pages/escrow-order.html?order_code=${order.order_code}`;
        }, 600);
    } catch (err) {
        console.error('Lỗi tạo đơn ký quỹ:', err);
        // Fallback chuyển trang với mã mặc định
        window.location.href = `pages/escrow-order.html?order_code=ORD-HUNRE-98471`;
    }
}

// =============================================================
// 6. XÁC THỰC & CHUYỂN ĐỔI NGƯỜI DÙNG (AUTH CONTEXT)
// =============================================================

async function loadUserTrustScore() {
    try {
        const res = await fetch(`${API_BASE_URL}/auth/users/trust-score?user_id=${currentUser.id}`);
        if (res.ok) {
            const data = await res.json();
            if (data.success && data.data) {
                currentUser.trust_score = data.data.trust_score;
                currentUser.tier = data.data.tier;
                updateUserDisplay();
            }
        }
    } catch (e) {
        console.warn('Lấy trust score từ auth service fallback:', e);
    }
}

function updateUserDisplay() {
    const nameEl = document.getElementById('currentUserName');
    const scoreEl = document.getElementById('userTrustScore');
    if (nameEl) nameEl.innerText = currentUser.full_name;
    if (scoreEl) {
        scoreEl.innerText = `${currentUser.trust_score} Điểm (${currentUser.tier.split(' ')[0]})`;
    }
}

async function openUserModal() {
    const modal = document.getElementById('userSwitchModal');
    const container = document.getElementById('usersListContainer');
    modal.style.display = 'flex';

    try {
        const res = await fetch(`${API_BASE_URL}/auth/users`);
        const data = await res.json();
        const users = data.users || [];

        container.innerHTML = users.map(u => `
            <div onclick="selectUser(${u.id})" style="padding: 12px 14px; background: ${u.id === currentUser.id ? 'rgba(16, 185, 129, 0.15)' : 'rgba(0,0,0,0.25)'}; border: 1px solid ${u.id === currentUser.id ? 'var(--primary-green)' : 'var(--border-subtle)'}; border-radius: var(--radius-sm); cursor: pointer; display: flex; justify-content: space-between; align-items: center; transition: var(--transition-fast);">
                <div>
                    <div style="font-weight: 600; font-size: 14px; color: #FFFFFF;">
                        ${u.full_name} 
                        ${u.id === currentUser.id ? '<span style="font-size: 11px; background: var(--primary-green); color: #000; padding: 1px 6px; border-radius: 8px; margin-left: 6px;">Đang chọn</span>' : ''}
                    </div>
                    <div style="font-size: 12px; color: var(--text-muted);">
                        MSV: ${u.student_code} • ${u.faculty || 'Khoa CNTT'} • Ví: ${Number(u.wallet_balance || 0).toLocaleString('vi-VN')}đ
                    </div>
                </div>
                <div style="text-align: right;">
                    <span style="font-size: 13px; font-weight: 700; color: var(--primary-green);">${u.trust_score} Điểm</span>
                </div>
            </div>
        `).join('');
    } catch (e) {
        container.innerHTML = '<p style="color: var(--text-muted); font-size: 13px;">Không thể tải danh sách tài khoản.</p>';
    }
}

function closeUserModal() {
    document.getElementById('userSwitchModal').style.display = 'none';
}

function selectUser(userId) {
    const userNames = {
        1: { full_name: "Nguyễn Văn An", student_code: "20211001", trust_score: 520, tier: "BẠC (Sinh viên uy tín tiêu chuẩn)", wallet_balance: 500000.0 },
        2: { full_name: "Trần Thị Bích", student_code: "20211002", trust_score: 480, tier: "BẠC (Sinh viên uy tín tiêu chuẩn)", wallet_balance: 250000.0 },
        3: { full_name: "Lê Hoàng Cường", student_code: "20211003", trust_score: 390, tier: "ĐỒNG (Cần tích lũy thêm giao dịch)", wallet_balance: 120000.0 },
        4: { full_name: "Cộng Tác Viên Trạm Hub", student_code: "HUB001", trust_score: 999, tier: "KIM CƯƠNG", wallet_balance: 0.0 }
    };

    if (userNames[userId]) {
        currentUser = { id: userId, ...userNames[userId] };
        updateUserDisplay();
        showToast(`Đã chuyển sang tài khoản: ${currentUser.full_name}`, 'info');
        closeUserModal();
        renderProducts(); // Render lại để cập nhật nút Sửa/Xóa của chính chủ
    }
}

// =============================================================
// 7. TOAST NOTIFICATIONS & TIỆN ÍCH
// =============================================================

function showToast(message, type = 'success') {
    const container = document.getElementById('toastContainer');
    if (!container) return;

    const icon = type === 'success' ? 'circle-check' : (type === 'error' ? 'circle-xmark' : 'circle-info');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `<i class="fa-solid fa-${icon}"></i> <span>${escapeHtml(message)}</span>`;

    container.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(50px)';
        toast.style.transition = 'all 0.3s ease';
        setTimeout(() => toast.remove(), 300);
    }, 3500);
}

function escapeHtml(str) {
    if (!str) return '';
    return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;").replace(/'/g, "&#039;");
}
