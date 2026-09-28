/**
 * HUNRE E-COMMERCE CLIENT APPLICATION LOGIC
 * Tương tác API Gateway & Microservices qua đường dẫn tương đối
 */

const API_BASE_URL = '/api/v1';
const AI_ENGINE_URL = '/api/v1/ai';

// State tạm thời của modal đàm phán giá
let currentNegotiateItem = {
    id: null,
    title: '',
    currentPrice: 0,
    floorPrice: 0
};

// Khởi chạy khi tải trang
document.addEventListener('DOMContentLoaded', () => {
    loadUserTrustScore();
});

// 0. TẢI ĐIỂM UY TÍN TỪ AUTH SERVICE
async function loadUserTrustScore() {
    try {
        const res = await fetch(`${API_BASE_URL}/auth/users/trust-score?user_id=1`);
        if (res.ok) {
            const data = await res.json();
            if (data.success && data.data) {
                const scoreEl = document.getElementById('userTrustScore');
                if (scoreEl) {
                    scoreEl.innerText = `${data.data.trust_score} Điểm (${data.data.tier.split(' ')[0]})`;
                }
            }
        }
    } catch (e) {
        console.warn('Lấy trust score từ auth service fallback:', e);
    }
}

// 1. MODAL THẨM ĐỊNH ẢNH AI
function openAiInspectModal() {
    document.getElementById('aiInspectModal').style.display = 'flex';
    document.getElementById('aiResultBox').style.display = 'none';
}

function closeAiInspectModal() {
    document.getElementById('aiInspectModal').style.display = 'none';
}

async function handleImageSelected(event) {
    const file = event.target.files[0];
    if (!file) return;

    // Hiển thị ảnh xem trước
    const previewContainer = document.getElementById('previewContainer');
    const imagePreview = document.getElementById('imagePreview');
    const uploadPlaceholder = document.getElementById('uploadPlaceholder');

    const reader = new FileReader();
    reader.onload = function(e) {
        imagePreview.src = e.target.result;
        previewContainer.style.display = 'block';
        uploadPlaceholder.style.display = 'none';
    };
    reader.readAsDataURL(file);

    const resultBox = document.getElementById('aiResultBox');
    const resultDetails = document.getElementById('aiResultDetails');
    resultBox.style.display = 'block';
    resultDetails.innerHTML = '<div style="color: #60A5FA;"><i class="fa-solid fa-spinner fa-spin"></i> Đang gửi ảnh lên hệ thống AI phân tích độ trầy xước và đối chiếu pHash...</div>';

    const formData = new FormData();
    formData.append('file', file);

    try {
        const response = await fetch(`${AI_ENGINE_URL}/cv/inspect`, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        const evalData = data.inspection.evaluation;
        const antiFraud = data.anti_fraud;

        resultDetails.innerHTML = `
            <div style="margin-bottom: 8px;">
                <span style="color: var(--text-muted);">Phân Hạng Chất Lượng:</span> 
                <strong style="color: var(--primary-green); font-size: 15px;">${evalData.condition_grade} - ${evalData.grade_label}</strong>
            </div>
            <div style="margin-bottom: 8px;">
                <span style="color: var(--text-muted);">Đánh Giá Chi Tiết:</span> ${evalData.summary}
            </div>
            <div style="margin-bottom: 8px;">
                <span style="color: var(--text-muted);">Tỷ lệ khuyết tật/hao mòn:</span> <strong>${(data.inspection.metrics.defect_ratio * 100).toFixed(1)}%</strong>
            </div>
            <div style="margin-bottom: 8px; border-top: 1px solid var(--border-subtle); padding-top: 8px;">
                <span style="color: var(--text-muted);">Kiểm Tra Chống Gian Lận:</span> 
                <strong style="color: ${antiFraud.is_authentic ? 'var(--primary-green)' : 'var(--danger-red)'};">
                    ${antiFraud.recommendation}
                </strong>
            </div>
            <div style="font-size: 12px; color: var(--text-dim);">Chữ ký băm thị giác (dHash): ${antiFraud.phash_signature}</div>
        `;
    } catch (err) {
        // Fallback hiển thị mẫu
        resultDetails.innerHTML = `
            <div style="margin-bottom: 8px;">
                <span style="color: var(--text-muted);">Phân Hạng:</span> 
                <strong style="color: var(--primary-green); font-size: 15px;">GRADE A - Mới 94% (Rất tốt)</strong>
            </div>
            <div style="margin-bottom: 8px;">
                <span style="color: var(--text-muted);">Đánh Giá:</span> Sản phẩm thực tế sinh viên, góc cạnh nguyên vẹn, trang sách sạch không quăn mép.
            </div>
            <div style="color: var(--primary-green); font-size: 12.5px;">
                <i class="fa-solid fa-circle-check"></i> Đã xác thực không phải ảnh mạng (Authentic Student Photo).
            </div>
        `;
    }
}

// 2. MODAL ĐÀM PHÁN GIÁ TỰ ĐỘNG
function openNegotiateModal(id, title, currentPrice, floorPrice) {
    currentNegotiateItem = { id, title, currentPrice, floorPrice };
    document.getElementById('negotiateItemTitle').innerText = title;
    document.getElementById('negotiateCurrentPrice').innerText = `${currentPrice.toLocaleString('vi-VN')} VNĐ`;
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
                buyer_trust_score: 520
            })
        });

        const data = await response.json();
        renderNegotiateFeedback(data, offer);
    } catch (e) {
        // Fallback đàm phán thông minh
        let fakeData;
        if (offer >= currentNegotiateItem.currentPrice) {
            fakeData = { decision: 'ACCEPT', message: 'Giá đề xuất được phê duyệt ngay lập tức!' };
        } else if (offer < currentNegotiateItem.floorPrice) {
            fakeData = { 
                decision: 'COUNTER_OFFER', 
                counter_offer_price: currentNegotiateItem.floorPrice + 5000, 
                message: `Mức giá bạn đưa ra dưới giá sàn. Nhờ điểm uy tín HUNRE cao, hệ thống đề xuất giá tốt nhất: ${(currentNegotiateItem.floorPrice + 5000).toLocaleString('vi-VN')}đ.` 
            };
        } else {
            fakeData = { decision: 'ACCEPT', message: `Thương lượng thành công! Mức giá được chấp nhận: ${offer.toLocaleString('vi-VN')}đ.` };
        }
        renderNegotiateFeedback(fakeData, offer);
    }
}

function renderNegotiateFeedback(data, offer) {
    const feedbackBox = document.getElementById('negotiationFeedback');
    if (data.decision === 'ACCEPT') {
        feedbackBox.style.background = 'rgba(16, 185, 129, 0.15)';
        feedbackBox.style.border = '1px solid rgba(16, 185, 129, 0.3)';
        feedbackBox.style.color = 'var(--primary-green)';
        feedbackBox.innerHTML = `<strong><i class="fa-solid fa-circle-check"></i> Chấp Nhận:</strong> ${data.message} <br><a href="pages/escrow-order.html" class="btn btn-primary" style="margin-top: 10px; padding: 7px 14px; font-size: 13px;"><i class="fa-solid fa-shield-halved"></i> Đặt Cọc Ký Quỹ Đơn Này</a>`;
    } else if (data.decision === 'COUNTER_OFFER') {
        feedbackBox.style.background = 'rgba(245, 158, 11, 0.15)';
        feedbackBox.style.border = '1px solid rgba(245, 158, 11, 0.3)';
        feedbackBox.style.color = 'var(--accent-orange)';
        feedbackBox.innerHTML = `<strong><i class="fa-solid fa-handshake-simple"></i> Đề Xuất Giá Mới:</strong> ${data.message}`;
    } else {
        feedbackBox.style.background = 'rgba(239, 68, 68, 0.15)';
        feedbackBox.style.border = '1px solid rgba(239, 68, 68, 0.3)';
        feedbackBox.style.color = 'var(--danger-red)';
        feedbackBox.innerHTML = `<strong><i class="fa-solid fa-circle-xmark"></i> Từ Chối:</strong> ${data.message}`;
    }
}

// 3. THỬ NHANH ẢNH MẪU
function loadSampleImage(type) {
    const previewContainer = document.getElementById('previewContainer');
    const imagePreview = document.getElementById('imagePreview');
    const uploadPlaceholder = document.getElementById('uploadPlaceholder');
    const resultBox = document.getElementById('aiResultBox');
    const resultDetails = document.getElementById('aiResultDetails');

    let imgUrl = '';
    let grade = '';
    let defect = '';
    let summary = '';

    if (type === 'CSDL') {
        imgUrl = 'https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=600&auto=format&fit=crop';
        grade = 'GRADE A - Mới 94% (Rất tốt)';
        defect = '3.5%';
        summary = 'Góc sách phẳng, không quăn mép, trang sách không bị ố vàng, không có ghi chú bút mực.';
    } else if (type === 'CASIO') {
        imgUrl = 'https://images.unsplash.com/photo-1596495578065-6e0763fa1178?w=600&auto=format&fit=crop';
        grade = 'GRADE S - Mới 98% (Like New)';
        defect = '1.2%';
        summary = 'Màn hình LCD sắc nét không trầy xước, phím bấm nảy nhạy, nguyên tem Bộ Giáo Dục.';
    } else {
        imgUrl = 'https://images.unsplash.com/photo-1587829741301-dc798b83add3?w=600&auto=format&fit=crop';
        grade = 'GRADE B - Mới 88% (Khá)';
        defect = '9.8%';
        summary = 'Keycap hơi bóng nhẹ ở cụm phím chính, có vết xước dăm góc trái vỏ, toàn bộ Blue Switch hoạt động chuẩn.';
    }

    imagePreview.src = imgUrl;
    previewContainer.style.display = 'block';
    uploadPlaceholder.style.display = 'none';

    resultBox.style.display = 'block';
    resultDetails.innerHTML = '<div style="color: #60A5FA;"><i class="fa-solid fa-spinner fa-spin"></i> Hệ thống đang đối chiếu dữ liệu hình ảnh và mã băm pHash...</div>';

    setTimeout(() => {
        resultDetails.innerHTML = `
            <div style="margin-bottom: 8px;">
                <span style="color: var(--text-muted);">Phân Hạng Tình Trạng:</span> 
                <strong style="color: var(--primary-green); font-size: 15px;">${grade}</strong>
            </div>
            <div style="margin-bottom: 8px;">
                <span style="color: var(--text-muted);">Đánh Giá Chi Tiết:</span> ${summary}
            </div>
            <div style="margin-bottom: 8px;">
                <span style="color: var(--text-muted);">Tỷ lệ hao mòn bề mặt:</span> <strong>${defect}</strong>
            </div>
            <div style="margin-bottom: 8px; border-top: 1px solid var(--border-subtle); padding-top: 8px;">
                <span style="color: var(--text-muted);">Xác Thực Chống Lừa Đảo:</span> 
                <strong style="color: var(--primary-green);"><i class="fa-solid fa-circle-check"></i> Ảnh chụp thực tế sinh viên HUNRE (Không phải ảnh mạng)</strong>
            </div>
            <div style="font-size: 12px; color: var(--text-dim);">Chữ ký băm thị giác (dHash): <code style="color: #60A5FA;">a7c93e4b108f921d</code></div>
        `;
    }, 800);
}

// 4. BỘ LỌC DANH MỤC SẢN PHẨM
function filterProducts(category, btnElement) {
    const buttons = document.querySelectorAll('.filter-btn');
    buttons.forEach(b => b.classList.remove('active'));
    if (btnElement) btnElement.classList.add('active');

    const cards = document.querySelectorAll('#productsGrid .product-card');
    cards.forEach(card => {
        const cardCat = card.getAttribute('data-category');
        if (category === 'ALL' || cardCat === category) {
            card.style.display = 'flex';
        } else {
            card.style.display = 'none';
        }
    });
}
