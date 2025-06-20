/**
 * admin_tours.js
 * Функции для управления турами в админ-панели.
 */

/* eslint-disable */
(() => {
    const API_PREFIX = '/api';

    // Утилита для показа уведомлений (simple alert fallback)
    function notify(msg, type = 'success') {
        if (window.showNotification) {
            // если подключена глобальная функция из admin.js
            window.showNotification(msg, type);
        } else {
            alert(msg);
        }
    }

    // ---------- Добавление тура ----------
    const addTourForm = document.getElementById('addTourForm');
    if (addTourForm) {
        addTourForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            e.stopPropagation();
            console.log('[admin_tours] submit form');
            const formData = new FormData(addTourForm);
            const payload = Object.fromEntries(formData.entries());

            ['base_price', 'duration_days', 'max_tourists', 'available_count', 'stars'].forEach(k => {
                if (payload[k]) payload[k] = Number(payload[k]);
            });

            const imageInput = addTourForm.querySelector('input[name="image"]');
            if (imageInput && imageInput.files.length > 0) {
                const fd = new FormData();
                fd.append('image', imageInput.files[0]);
                const resUp = await fetch(`${API_PREFIX}/tours/upload-image`, {method:'POST',body:fd,credentials:'same-origin'});
                if (!resUp.ok) { alert('Ошибка загрузки изображения'); return; }
                const {url} = await resUp.json();
                payload.image_url = url;
            }

            const res = await fetch(`${API_PREFIX}/tours/`, {
                method:'POST',
                headers:{'Content-Type':'application/json'},
                credentials:'same-origin',
                body: JSON.stringify(payload)
            });
            if (!res.ok) {
                const err = await res.json().catch(()=>({detail:'Ошибка'}));
                alert(err.detail || 'Ошибка добавления тура');
                return;
            }
            // hide modal
            const modalEl = document.getElementById('addTourModal');
            if (modalEl) {
                const modalObj = bootstrap.Modal.getInstance(modalEl) || new bootstrap.Modal(modalEl);
                modalObj.hide();
            }
            location.reload();
        });
    }

    // ---------- Удаление тура ----------
    document.querySelectorAll('.btn-delete-tour').forEach(btn => {
        btn.addEventListener('click', async () => {
            const id = btn.dataset.tourId;
            if (!id || !confirm(`Удалить тур #${id}?`)) return;
            const res = await fetch(`${API_PREFIX}/tours/${id}`, {method:'DELETE',credentials:'same-origin'});
            if (!res.ok) { alert('Ошибка удаления'); return; }
            document.querySelector(`tr[data-tour-id="${id}"]`)?.remove();
        });
    });
})(); 