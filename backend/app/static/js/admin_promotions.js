/**
 * admin_promotions.js
 * Управление акциями/скидками в админ-панели
 */

(() => {
    const API_PREFIX = '/api';

    // ======= Helpers ========
    function notify(msg, type = 'success') {
        if (window.showNotification) {
            window.showNotification(msg, type);
        } else {
            console.log(`[${type}] ${msg}`);
        }
    }

    // ======= Create promotion ========
    const createForm = document.getElementById('createPromotionForm');
    if (createForm) {
        createForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const fd = new FormData(createForm);
            const payload = {
                name: fd.get('name'),
                description: fd.get('description') || undefined,
                discount_type: fd.get('discount_type'),
                value: parseFloat(fd.get('value')),
                valid_from: fd.get('valid_from') || null,
                valid_to: fd.get('valid_to') || null,
                is_active: fd.get('is_active') === 'on',
            };

            const tourSelect = createForm.querySelector('#promoTourSelect');
            if (tourSelect) {
                const ids = Array.from(tourSelect.selectedOptions).map(o => Number(o.value));
                if (!ids.length) {
                    alert('Выберите хотя бы один тур, который участвует в акции');
                    return;
                }
                payload.tour_ids = ids;
            }

            // image upload
            const imgInput = createForm.querySelector('input[name="image"]');
            if (imgInput && imgInput.files.length > 0) {
                const imgFd = new FormData();
                imgFd.append('image', imgInput.files[0]);
                const upRes = await fetch(`${API_PREFIX}/discounts/upload-image`, {method:'POST', body: imgFd, credentials:'same-origin'});
                if (!upRes.ok) { alert('Ошибка загрузки изображения'); return; }
                const { url } = await upRes.json();
                payload.image_url = url;
            }

            try {
                const res = await fetch(`${API_PREFIX}/discounts/`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    credentials: 'same-origin',
                    body: JSON.stringify(payload),
                });
                if (!res.ok) {
                    const err = await res.json().catch(() => ({}));
                    throw new Error(err.detail || 'Ошибка создания акции');
                }
                notify('Акция создана');
                bootstrap.Modal.getInstance(document.getElementById('createPromotionModal')).hide();
                location.reload();
            } catch (err) {
                alert(err.message || err);
            }
        });
    }

    // ======= Delete promotion ========
    const deleteModal = document.getElementById('deletePromotionModal');
    if (deleteModal) {
        deleteModal.addEventListener('show.bs.modal', (event) => {
            const button = event.relatedTarget;
            if (!button) return;
            const id = button.getAttribute('data-promo-id');
            const name = button.getAttribute('data-promo-name');
            deleteModal.querySelector('#promoToDeleteName').textContent = name;
            const confirmBtn = deleteModal.querySelector('#confirmDeletePromoBtn');
            confirmBtn.dataset.promoId = id;
        });

        const confirmBtn = deleteModal.querySelector('#confirmDeletePromoBtn');
        confirmBtn?.addEventListener('click', async () => {
            const id = confirmBtn.dataset.promoId;
            if (!id) return;
            confirmBtn.disabled = true;
            try {
                const res = await fetch(`${API_PREFIX}/discounts/${id}`, {
                    method: 'DELETE',
                    credentials: 'same-origin',
                });
                if (!res.ok) throw new Error('Ошибка удаления акции');
                notify('Акция удалена', 'info');
                location.reload();
            } catch (err) {
                alert(err.message || err);
            } finally {
                confirmBtn.disabled = false;
            }
        });
    }

    // ======= Edit promotion ========
    const editModalEl = document.getElementById('editPromotionModal');
    if (editModalEl) {
        editModalEl.addEventListener('show.bs.modal', async (e) => {
            const btn = e.relatedTarget;
            if (!btn) return;
            const row = btn.closest('tr');
            const id = row?.children[0]?.textContent.trim();
            const name = row?.children[1]?.textContent.trim();
            const type = row?.children[2]?.textContent.trim();
            const valueCell = row?.children[3]?.textContent.trim();
            const value = parseFloat(valueCell.replace(/[^0-9.]/g, ''));
            const isActive = row?.querySelector('.badge')?.classList.contains('bg-success');

            // fill form
            editModalEl.querySelector('#editPromoId').value = id;
            editModalEl.querySelector('#editPromoName').value = name;
            editModalEl.querySelector('#editPromoType').value = type;
            editModalEl.querySelector('#editPromoValue').value = value;
            editModalEl.querySelector('#editPromoActive').checked = !!isActive;

            // Reset selections
            const multiselect = editModalEl.querySelector('#editPromoTours');
            Array.from(multiselect.options).forEach(opt => (opt.selected = false));

            // Fetch tours already in promo to preselect
            try {
                const resp = await fetch(`${API_PREFIX}/tours?promotion=${id}&limit=100`, {credentials:'same-origin'});
                if (resp.ok) {
                    const data = await resp.json();
                    const ids = data.tours.map(t => t.id);
                    Array.from(multiselect.options).forEach(opt => {
                        if (ids.includes(Number(opt.value))) opt.selected = true;
                    });
                }
            } catch(err) { console.warn(err); }
        });

        // submit form
        const editForm = document.getElementById('editPromotionForm');
        editForm.addEventListener('submit', async (evt) => {
            evt.preventDefault();
            const fd = new FormData(editForm);
            const id = fd.get('id');
            const payload = {
                name: fd.get('name'),
                description: fd.get('description') || undefined,
                discount_type: fd.get('discount_type'),
                value: parseFloat(fd.get('value')),
                valid_from: fd.get('valid_from') || null,
                valid_to: fd.get('valid_to') || null,
                is_active: fd.get('is_active') === 'on',
            };
            // tours
            const multiselect = editForm.querySelector('#editPromoTours');
            const ids = Array.from(multiselect.selectedOptions).map(o=>Number(o.value));
            payload.tour_ids = ids;

            try {
                const res = await fetch(`${API_PREFIX}/discounts/${id}`, {
                    method:'PUT',
                    headers:{'Content-Type':'application/json'},
                    credentials:'same-origin',
                    body: JSON.stringify(payload)
                });
                if (!res.ok) throw new Error('Ошибка сохранения акции');
                notify('Акция обновлена');
                bootstrap.Modal.getInstance(editModalEl).hide();
                location.reload();
            } catch(err){ alert(err.message||err); }
        });
    }
})(); 