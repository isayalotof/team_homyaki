/**
 * Многошаговый поиск тура с drag & drop
 * 
 * Позволяет настроить маршрут, добавляя и удаляя города и места,
 * перетаскивая их в нужном порядке.
 */

document.addEventListener('DOMContentLoaded', function() {
    // Инициализация поискового мастера
    initSearchWizard();
});

/**
 * Инициализирует весь поисковый мастер
 */
function initSearchWizard() {
    const searchWizard = document.getElementById('search-wizard');
    if (!searchWizard) return;

    // Инициализация переменных
    const wizard = {
        currentStep: 1,
        totalSteps: 4,
        destinations: [], // Массив для хранения выбранных мест
        selectedDates: {
            start: null,
            end: null
        },
        parameters: {
            adults: 2,
            children: 0,
            budget: 50000,
            preferredTransport: 'any', // 'train', 'plane', 'bus', 'any'
            accommodationStars: 3,
            accommodationType: 'hotel', // 'hotel', 'hostel', 'apartment'
            includeMeals: true,
            includeExcursions: true
        }
    };
    
    // Сохраняем ссылку на объект wizard в глобальной переменной
    window.currentWizard = wizard;
    window.searchWizardData = window.searchWizardData || {};

    // Инициализация шагов
    initStep1(wizard);
    initStep2(wizard);
    initStep3(wizard);
    initStep4(wizard);

    // Обработчики кнопок навигации
    setupNavigation(wizard);

    // Отображаем первый шаг
    showStep(wizard, 1);
}

/**
 * Инициализирует первый шаг - выбор городов и достопримечательностей
 */
function initStep1(wizard) {
    // Получаем контейнеры для доступных и выбранных мест
    const availableItems = document.getElementById('available-destinations');
    const selectedItems = document.getElementById('selected-destinations');
    
    if (!availableItems || !selectedItems) return;

    // Загружаем доступные места с сервера
    loadAvailableDestinations(availableItems);

    // Настраиваем перетаскивание (drag and drop)
    setupDragAndDrop(availableItems, selectedItems, wizard);

    // Обработчик для панели поиска мест
    const searchInput = document.getElementById('destination-search');
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            filterDestinations(this.value, availableItems);
        });
    }
    
    // Обработчик для кнопки очистки маршрута
    const clearRouteButton = document.getElementById('clear-route');
    if (clearRouteButton) {
        clearRouteButton.addEventListener('click', function() {
            // Очищаем контейнер с выбранными местами
            while (selectedItems.lastChild && !selectedItems.lastChild.classList.contains('destination-container-header')) {
                selectedItems.removeChild(selectedItems.lastChild);
            }
            // Обновляем визуализацию маршрута
            updateRouteVisualization();
        });
    }
}

/**
 * Загружает доступные места с сервера
 */
function loadAvailableDestinations(container) {
    // Показываем индикатор загрузки
    container.innerHTML = '<div class="text-center py-4"><div class="spinner-border text-primary" role="status"><span class="visually-hidden">Загрузка...</span></div><p class="mt-2">Загрузка доступных направлений...</p></div>';
    
    // Делаем запрос к API для получения доступных направлений
    fetch('/api/v1/search/destinations')
        .then(response => {
            if (!response.ok) {
                throw new Error('Ошибка при загрузке направлений');
            }
            return response.json();
        })
        .then(destinations => {
            // Очищаем контейнер
            container.innerHTML = '';
            
            // Если нет направлений, показываем сообщение
            if (!destinations || destinations.length === 0) {
                container.innerHTML = '<div class="text-center py-4"><p>Нет доступных направлений</p></div>';
                return;
            }
            
            // Добавляем заголовок
            const header = document.createElement('div');
            header.className = 'destination-container-header';
            header.innerHTML = '<h5 class="mb-0">Доступные места</h5>';
            container.appendChild(header);
            
            // Создаем элементы для каждого места
            destinations.forEach(dest => {
                const item = createDestinationElement(dest);
                container.appendChild(item);
            });
        })
        .catch(error => {
            console.error('Ошибка при загрузке направлений:', error);
            container.innerHTML = `
                <div class="text-center py-4">
                    <div class="alert alert-danger" role="alert">
                        <i class="fas fa-exclamation-triangle me-2"></i>
                        Не удалось загрузить направления. Пожалуйста, попробуйте позже.
                    </div>
                    <button class="btn btn-outline-primary mt-2" onclick="loadAvailableDestinations(this.parentNode.parentNode)">
                        <i class="fas fa-sync-alt me-2"></i>Повторить попытку
                    </button>
                </div>
            `;
        });
}

/**
 * Создает DOM-элемент для места назначения
 */
function createDestinationElement(destination) {
    const item = document.createElement('div');
    item.className = 'destination-item';
    item.draggable = true;
    item.dataset.id = destination.id;
    item.dataset.type = destination.type;
    item.dataset.name = destination.name;

    const icon = destination.type === 'city' ? 'fa-city' : 'fa-landmark';
    
    // Всегда используем изображения туров вместо изображений направлений
    const tourImageBase = '/static/images/tours/';
    const tourImages = [
        'tour_0cb780db5ec24926868a160cba4be43b.png',
        'tour_216569d19a1c4d008f6cd7ae337e6489.jpg',
        'tour_21fe1d694c87466999dd063d000401be.jpg',
        'tour_30ad228907a34d13be16c5a34a767acf.png',
        'tour_3a8167e27a2845c18ef748a50f6731f3.png',
        'tour_5f705c2184f345d9b098f51b7b5245a3.jpg',
        'tour_721e5f5c585844058bd74f3126a6c201.jpeg',
        'tour_75bf23fdc97645b4a41c87aaded8464c.jpeg',
        'tour_7cf5fe2b4d9c4e64b6dbec4b7b4fa0c7.jpg',
        'tour_9b566f00a0924cf186c4b4dac49832c1.jpg',
        'tour_a30db0615c2244d39b9a62939c6b7334.jpg',
        'tour_c62b2ffbdb4b449c9b1fce5384e0a095.png',
    ];
    
    // Выбираем изображение в зависимости от id направления
    const imageIndex = destination.id % tourImages.length;
    const imagePath = tourImageBase + tourImages[imageIndex];
    
    item.innerHTML = `
        <div class="destination-thumb" style="background-image: url('${imagePath}')"></div>
        <div class="destination-info">
            <h5>${destination.name}</h5>
            <span class="badge ${destination.type === 'city' ? 'bg-primary' : 'bg-success'}">
                <i class="fas ${icon}"></i> ${destination.type === 'city' ? 'Город' : 'Достопримечательность'}
            </span>
        </div>
        <div class="destination-actions">
            <button class="btn btn-sm btn-outline-secondary add-destination" title="Добавить">
                <i class="fas fa-plus"></i>
            </button>
        </div>
    `;

    // Добавляем обработчик нажатия на кнопку добавления
    const addButton = item.querySelector('.add-destination');
    if (addButton) {
        addButton.addEventListener('click', function(e) {
            e.preventDefault();
            const selectedContainer = document.getElementById('selected-destinations');
            if (selectedContainer) {
                // Клонируем элемент для выбранных мест
                const clonedItem = item.cloneNode(true);
                
                // Меняем кнопку "Добавить" на "Удалить"
                const actionsDiv = clonedItem.querySelector('.destination-actions');
                actionsDiv.innerHTML = `
                    <button class="btn btn-sm btn-outline-danger remove-destination" title="Удалить">
                        <i class="fas fa-trash"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-secondary move-up" title="Переместить выше">
                        <i class="fas fa-arrow-up"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-secondary move-down" title="Переместить ниже">
                        <i class="fas fa-arrow-down"></i>
                    </button>
                `;
                
                // Добавляем обработчики для новых кнопок
                setupSelectedItemButtons(clonedItem);
                
                // Добавляем в список выбранных
                selectedContainer.appendChild(clonedItem);
                
                // Обновляем визуальные элементы маршрута
                updateRouteVisualization();
            }
        });
    }

    // Добавляем обработчики для drag&drop
    item.addEventListener('dragstart', function(e) {
        e.dataTransfer.setData('text/plain', destination.id);
        this.classList.add('dragging');
    });

    item.addEventListener('dragend', function() {
        this.classList.remove('dragging');
    });

    return item;
}

/**
 * Настраивает кнопки для выбранного элемента маршрута
 */
function setupSelectedItemButtons(item) {
    // Кнопка удаления
    const removeButton = item.querySelector('.remove-destination');
    if (removeButton) {
        removeButton.addEventListener('click', function(e) {
            e.preventDefault();
            item.remove();
            updateRouteVisualization();
        });
    }
    
    // Кнопка перемещения вверх
    const upButton = item.querySelector('.move-up');
    if (upButton) {
        upButton.addEventListener('click', function(e) {
            e.preventDefault();
            const prev = item.previousElementSibling;
            if (prev) {
                item.parentNode.insertBefore(item, prev);
                updateRouteVisualization();
            }
        });
    }
    
    // Кнопка перемещения вниз
    const downButton = item.querySelector('.move-down');
    if (downButton) {
        downButton.addEventListener('click', function(e) {
            e.preventDefault();
            const next = item.nextElementSibling;
            if (next) {
                item.parentNode.insertBefore(next, item);
                updateRouteVisualization();
            }
        });
    }
}

/**
 * Настраивает функционал drag and drop
 */
function setupDragAndDrop(sourceContainer, targetContainer, wizard) {
    // Обработчик перетаскивания над контейнером назначения
    targetContainer.addEventListener('dragover', function(e) {
        e.preventDefault();
        const dragging = document.querySelector('.dragging');
        if (dragging) {
            this.classList.add('drag-over');
        }
    });
    
    // Обработчик выхода перетаскивания из зоны контейнера
    targetContainer.addEventListener('dragleave', function() {
        this.classList.remove('drag-over');
    });
    
    // Обработчик сброса элемента
    targetContainer.addEventListener('drop', function(e) {
        e.preventDefault();
        this.classList.remove('drag-over');
        
        const id = e.dataTransfer.getData('text/plain');
        const sourceItem = sourceContainer.querySelector(`[data-id="${id}"]`);
        
        if (sourceItem) {
            // Клонируем элемент для выбранных мест
            const clonedItem = sourceItem.cloneNode(true);
            
            // Меняем кнопку "Добавить" на "Удалить"
            const actionsDiv = clonedItem.querySelector('.destination-actions');
            actionsDiv.innerHTML = `
                <button class="btn btn-sm btn-outline-danger remove-destination" title="Удалить">
                    <i class="fas fa-trash"></i>
                </button>
                <button class="btn btn-sm btn-outline-secondary move-up" title="Переместить выше">
                    <i class="fas fa-arrow-up"></i>
                </button>
                <button class="btn btn-sm btn-outline-secondary move-down" title="Переместить ниже">
                    <i class="fas fa-arrow-down"></i>
                </button>
            `;
            
            // Добавляем обработчики для новых кнопок
            setupSelectedItemButtons(clonedItem);
            
            // Находим позицию, куда вставить элемент
            // (если перетаскиваем между существующими элементами)
            const afterElement = getDragAfterElement(targetContainer, e.clientY);
            if (afterElement) {
                targetContainer.insertBefore(clonedItem, afterElement);
            } else {
                targetContainer.appendChild(clonedItem);
            }
            
            // Обновляем визуальные элементы маршрута
            updateRouteVisualization();
        }
    });
}

/**
 * Определяет, после какого элемента нужно вставить перетаскиваемый элемент
 */
function getDragAfterElement(container, y) {
    const items = [...container.querySelectorAll('.destination-item:not(.dragging)')];
    
    return items.reduce((closest, item) => {
        const box = item.getBoundingClientRect();
        const offset = y - box.top - box.height / 2;
        
        if (offset < 0 && offset > closest.offset) {
            return { offset: offset, element: item };
        } else {
            return closest;
        }
    }, { offset: Number.NEGATIVE_INFINITY }).element;
}

/**
 * Фильтрует места по поисковому запросу
 */
function filterDestinations(query, container) {
    query = query.toLowerCase();
    const items = container.querySelectorAll('.destination-item');
    
    items.forEach(item => {
        const name = item.dataset.name.toLowerCase();
        const type = item.dataset.type.toLowerCase();
        
        if (name.includes(query) || type.includes(query)) {
            item.style.display = '';
        } else {
            item.style.display = 'none';
        }
    });
}

/**
 * Обновляет визуальное представление маршрута
 */
function updateRouteVisualization() {
    const selectedItems = document.getElementById('selected-destinations');
    const routeVisualization = document.getElementById('route-visualization');
    
    if (!selectedItems || !routeVisualization) return;
    
    // Очищаем визуализацию маршрута
    routeVisualization.innerHTML = '';
    
    const items = selectedItems.querySelectorAll('.destination-item');
    if (items.length === 0) {
        routeVisualization.innerHTML = '<div class="text-center text-muted">Добавьте места в ваш маршрут, чтобы увидеть его здесь</div>';
        return;
    }
    
    // Создаем элементы для визуализации маршрута
    items.forEach((item, index) => {
        const name = item.dataset.name;
        const type = item.dataset.type;
        const icon = type === 'city' ? 'fa-city' : 'fa-landmark';
        
        const routeItem = document.createElement('div');
        routeItem.className = 'route-item';
        
        routeItem.innerHTML = `
            <div class="route-point">
                <div class="route-point-number">${index + 1}</div>
                <div class="route-point-icon">
                    <i class="fas ${icon}"></i>
                </div>
            </div>
            <div class="route-name">${name}</div>
        `;
        
        routeVisualization.appendChild(routeItem);
        
        // Добавляем соединительную линию между точками, кроме последней
        if (index < items.length - 1) {
            const connector = document.createElement('div');
            connector.className = 'route-connector';
            routeVisualization.appendChild(connector);
        }
    });
    
    // Обновляем массив мест в объекте маршрута
    updateDestinationsArray();
}

/**
 * Обновляет массив выбранных мест
 */
function updateDestinationsArray() {
    const selectedItems = document.getElementById('selected-destinations');
    if (!selectedItems) return;
    
    const items = selectedItems.querySelectorAll('.destination-item');
    const destinations = [];
    
    items.forEach((item, index) => {
        destinations.push({
            id: parseInt(item.dataset.id, 10),
            name: item.dataset.name,
            type: item.dataset.type,
            order: index + 1
        });
    });
    
    // Сохраняем в глобальной переменной для использования в других функциях
    window.searchWizardData = window.searchWizardData || {};
    window.searchWizardData.destinations = destinations;
    
    // Также обновляем в объекте wizard, если он доступен
    if (window.currentWizard) {
        window.currentWizard.destinations = destinations;
    }
}

/**
 * Инициализирует второй шаг - выбор дат поездки
 */
function initStep2(wizard) {
    const dateRangeInput = document.getElementById('date-range');
    if (!dateRangeInput) return;
    
    // Инициализируем выбор даты с помощью flatpickr
    const fp = flatpickr(dateRangeInput, {
        mode: "range",
        dateFormat: "d.m.Y",
        minDate: "today",
        locale: "ru",
        disableMobile: true,
        showMonths: window.innerWidth > 768 ? 2 : 1,
        onChange: function(selectedDates, dateStr) {
            if (selectedDates.length === 2) {
                wizard.selectedDates.start = selectedDates[0];
                wizard.selectedDates.end = selectedDates[1];
                updateTripDuration(selectedDates[0], selectedDates[1]);
            }
        }
    });
    
    // Настраиваем кнопки быстрого выбора дат
    setupQuickDateButtons(fp);
}

/**
 * Настраивает кнопки быстрого выбора дат
 */
function setupQuickDateButtons(datepicker) {
    const quickDateButtons = document.querySelectorAll('.quick-date-btn');
    
    quickDateButtons.forEach(button => {
        button.addEventListener('click', function() {
            const days = parseInt(this.dataset.days, 10);
            if (isNaN(days)) return;
            
            const startDate = new Date();
            const endDate = new Date();
            endDate.setDate(endDate.getDate() + days - 1);
            
            datepicker.setDate([startDate, endDate]);
            updateTripDuration(startDate, endDate);
        });
    });
}

/**
 * Обновляет информацию о длительности поездки
 */
function updateTripDuration(startDate, endDate) {
    const durationInfo = document.getElementById('trip-duration');
    if (!durationInfo) return;
    
    // Вычисляем длительность в днях
    const diffTime = Math.abs(endDate - startDate);
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    
    durationInfo.textContent = `Длительность поездки: ${diffDays} ${getDaysWord(diffDays)}`;
}

/**
 * Возвращает правильное склонение слова "день"
 */
function getDaysWord(days) {
    const remainder = days % 10;
    
    if (days >= 11 && days <= 19) {
        return 'дней';
    } else if (remainder === 1) {
        return 'день';
    } else if (remainder >= 2 && remainder <= 4) {
        return 'дня';
    } else {
        return 'дней';
    }
}

/**
 * Инициализирует третий шаг - информация о путешественниках
 */
function initStep3(wizard) {
    // Инициализация счетчиков для взрослых и детей
    const adultsCounter = document.getElementById('adults-counter');
    const childrenCounter = document.getElementById('children-counter');
    
    if (adultsCounter) setupCounter(adultsCounter, 1, 10, 'adults');
    if (childrenCounter) setupCounter(childrenCounter, 0, 6, 'children');
    
    // Инициализация ползунка для бюджета
    const budgetSlider = document.getElementById('budget-slider');
    const budgetValue = document.getElementById('budget-value');
    
    if (budgetSlider && budgetValue) {
        budgetSlider.addEventListener('input', function() {
            const value = parseInt(this.value, 10);
            budgetValue.textContent = `${value.toLocaleString()} ₽`;
            wizard.parameters.budget = value;
        });
    }
}

/**
 * Настраивает счетчик с кнопками + и -
 */
function setupCounter(container, min, max, paramName) {
    const plusBtn = container.querySelector('.plus-btn');
    const minusBtn = container.querySelector('.minus-btn');
    const valueDisplay = container.querySelector('.counter-value');
    
    let currentValue = parseInt(valueDisplay.textContent, 10);
    
    updateButtonStates();
    
    // Обработчик для кнопки +
    if (plusBtn) {
        plusBtn.addEventListener('click', function() {
            if (currentValue < max) {
                currentValue++;
                valueDisplay.textContent = currentValue;
                updateButtonStates();
                
                // Обновляем значение в объекте wizard
                window.searchWizardData = window.searchWizardData || {};
                window.searchWizardData.parameters = window.searchWizardData.parameters || {};
                window.searchWizardData.parameters[paramName] = currentValue;
            }
        });
    }
    
    // Обработчик для кнопки -
    if (minusBtn) {
        minusBtn.addEventListener('click', function() {
            if (currentValue > min) {
                currentValue--;
                valueDisplay.textContent = currentValue;
                updateButtonStates();
                
                // Обновляем значение в объекте wizard
                window.searchWizardData = window.searchWizardData || {};
                window.searchWizardData.parameters = window.searchWizardData.parameters || {};
                window.searchWizardData.parameters[paramName] = currentValue;
            }
        });
    }
    
    // Обновляет состояние кнопок (активна/неактивна)
    function updateButtonStates() {
        if (minusBtn) minusBtn.disabled = (currentValue <= min);
        if (plusBtn) plusBtn.disabled = (currentValue >= max);
    }
}

/**
 * Инициализирует четвертый шаг - предпочтения по туру
 */
function initStep4(wizard) {
    // Обработчики для переключателей типа транспорта
    const transportButtons = document.querySelectorAll('input[name="transport"]');
    transportButtons.forEach(button => {
        button.addEventListener('change', function() {
            wizard.parameters.preferredTransport = this.value;
        });
    });
    
    // Обработчик для рейтинга (звезд отеля)
    const starsRating = document.getElementById('accommodation-stars');
    if (starsRating) {
        starsRating.addEventListener('change', function() {
            wizard.parameters.accommodationStars = parseInt(this.value, 10);
        });
    }
    
    // Обработчики для типа проживания
    const accommodationTypes = document.querySelectorAll('input[name="accommodation-type"]');
    accommodationTypes.forEach(type => {
        type.addEventListener('change', function() {
            wizard.parameters.accommodationType = this.value;
        });
    });
    
    // Обработчики для дополнительных опций
    const mealCheckbox = document.getElementById('include-meals');
    if (mealCheckbox) {
        mealCheckbox.addEventListener('change', function() {
            wizard.parameters.includeMeals = this.checked;
        });
    }
    
    const excursionsCheckbox = document.getElementById('include-excursions');
    if (excursionsCheckbox) {
        excursionsCheckbox.addEventListener('change', function() {
            wizard.parameters.includeExcursions = this.checked;
        });
    }
}

/**
 * Настраивает навигацию между шагами
 */
function setupNavigation(wizard) {
    const prevButton = document.getElementById('prev-step');
    const nextButton = document.getElementById('next-step');
    const submitButton = document.getElementById('submit-search');
    
    if (!prevButton || !nextButton || !submitButton) return;
    
    // Обработчик для кнопки "Назад"
    prevButton.addEventListener('click', function() {
        if (wizard.currentStep > 1) {
            // Скрываем сообщения об ошибках при переходе на предыдущий шаг
            clearErrorMessages();
            showStep(wizard, wizard.currentStep - 1);
        }
    });
    
    // Обработчик для кнопки "Далее"
    nextButton.addEventListener('click', function() {
        if (wizard.currentStep < wizard.totalSteps) {
            // Проверяем валидность текущего шага
            if (validateCurrentStep(wizard)) {
                // Скрываем сообщения об ошибках при переходе на следующий шаг
                clearErrorMessages();
                showStep(wizard, wizard.currentStep + 1);
            }
        }
    });
    
    // Обработчик для кнопки отправки формы
    submitButton.addEventListener('click', function() {
        if (validateCurrentStep(wizard)) {
            submitSearchForm(wizard);
        }
    });
    
    // Обработчик для индикаторов шагов
    const stepIndicators = document.querySelectorAll('.step-indicator');
    stepIndicators.forEach(indicator => {
        indicator.addEventListener('click', function() {
            const stepNumber = parseInt(this.dataset.step, 10);
            if (stepNumber && stepNumber <= wizard.currentStep) {
                // Можно переходить только на текущий или пройденные шаги
                clearErrorMessages();
                showStep(wizard, stepNumber);
            }
        });
    });
}

/**
 * Очищает все сообщения об ошибках
 */
function clearErrorMessages() {
    const errorContainers = document.querySelectorAll('[id$="-error"]');
    errorContainers.forEach(container => {
        container.style.display = 'none';
        container.textContent = '';
    });
}

/**
 * Проверяет валидность текущего шага
 */
function validateCurrentStep(wizard) {
    switch (wizard.currentStep) {
        case 1:
            // Проверяем, что выбран хотя бы один пункт маршрута
            updateDestinationsArray();
            if (window.searchWizardData.destinations.length === 0) {
                const errorEl = document.getElementById('step-1-error');
                if (errorEl) {
                    errorEl.textContent = 'Пожалуйста, выберите хотя бы один пункт маршрута';
                    errorEl.style.display = 'block';
                }
                return false;
            }
            return true;
            
        case 2:
            // Проверяем, что выбраны даты поездки
            if (!wizard.selectedDates.start || !wizard.selectedDates.end) {
                const errorEl = document.getElementById('step-2-error');
                if (errorEl) {
                    errorEl.textContent = 'Пожалуйста, выберите даты поездки';
                    errorEl.style.display = 'block';
                }
                return false;
            }
            return true;
            
        case 3:
            // Проверяем количество путешественников (должен быть хотя бы один)
            if (wizard.parameters.adults + wizard.parameters.children < 1) {
                return false;
            }
            return true;
            
        case 4:
            // На последнем шаге нет специальных проверок
            return true;
            
        default:
            return true;
    }
}

/**
 * Отображает указанный шаг поискового мастера
 */
function showStep(wizard, stepNumber) {
    // Скрываем все шаги
    for (let i = 1; i <= wizard.totalSteps; i++) {
        const stepContainer = document.getElementById(`step-${i}`);
        if (stepContainer) {
            stepContainer.style.display = 'none';
        }
    }
    
    // Показываем запрошенный шаг
    const currentStep = document.getElementById(`step-${stepNumber}`);
    if (currentStep) {
        currentStep.style.display = 'block';
    }
    
    // Обновляем текущий шаг
    wizard.currentStep = stepNumber;
    
    // Обновляем индикатор прогресса
    updateStepIndicators(wizard);
    
    // Обновляем кнопки навигации
    updateNavigationButtons(wizard);
}

/**
 * Обновляет индикаторы шагов
 */
function updateStepIndicators(wizard) {
    const indicators = document.querySelectorAll('.step-indicator');
    
    indicators.forEach((indicator, index) => {
        // Удаляем все классы состояния
        indicator.classList.remove('active', 'completed');
        
        const stepNumber = index + 1;
        
        if (stepNumber === wizard.currentStep) {
            // Текущий шаг
            indicator.classList.add('active');
        } else if (stepNumber < wizard.currentStep) {
            // Завершенные шаги
            indicator.classList.add('completed');
        }
    });
}

/**
 * Обновляет кнопки навигации между шагами
 */
function updateNavigationButtons(wizard) {
    const prevBtn = document.getElementById('prev-step');
    const nextBtn = document.getElementById('next-step');
    const submitBtn = document.getElementById('submit-search');
    
    // Кнопка "Назад"
    if (prevBtn) {
        prevBtn.style.display = wizard.currentStep === 1 ? 'none' : 'inline-block';
    }
    
    // Кнопка "Далее"
    if (nextBtn) {
        nextBtn.style.display = wizard.currentStep < wizard.totalSteps ? 'inline-block' : 'none';
    }
    
    // Кнопка "Найти туры"
    if (submitBtn) {
        submitBtn.style.display = wizard.currentStep === wizard.totalSteps ? 'inline-block' : 'none';
    }
}

/**
 * Отправляет форму поиска на сервер
 */
function submitSearchForm(wizard) {
    // Собираем все данные из мастера
    updateDestinationsArray();
    
    // Создаем объект с данными для поиска
    const searchData = {
        destinations: window.searchWizardData.destinations,
        dates: {
            start: wizard.selectedDates.start ? formatDate(wizard.selectedDates.start) : null,
            end: wizard.selectedDates.end ? formatDate(wizard.selectedDates.end) : null
        },
        tourists: {
            adults: wizard.parameters.adults,
            children: wizard.parameters.children
        },
        budget: wizard.parameters.budget,
        preferences: {
            transport: wizard.parameters.preferredTransport,
            accommodation: {
                type: wizard.parameters.accommodationType,
                stars: wizard.parameters.accommodationStars
            },
            includeMeals: wizard.parameters.includeMeals,
            includeExcursions: wizard.parameters.includeExcursions
        }
    };
    
    console.log("Отправляем данные поиска:", searchData);
    
    // Показываем индикатор загрузки
    const wizardContainer = document.getElementById('search-wizard');
    if (wizardContainer) {
        wizardContainer.innerHTML = `
            <div class="text-center py-5">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Загрузка...</span>
                </div>
                <p class="mt-3">Перенаправляем на страницу с турами...</p>
            </div>
        `;
    }

    // Вместо отправки запроса на API, сразу перенаправляем на страницу с турами
    try {
        const searchParam = encodeURIComponent(JSON.stringify(searchData));
        console.log("Перенаправляем на:", '/tours?custom_search=1&wizard=1&search=' + searchParam);
        
        // Используем setTimeout для гарантированного перенаправления после отображения индикатора загрузки
        setTimeout(() => {
            window.location.href = '/tours?custom_search=1&wizard=1&search=' + searchParam;
        }, 500);
    } catch (error) {
        console.error('Ошибка при перенаправлении:', error);
        if (wizardContainer) {
            wizardContainer.innerHTML = `
                <div class="text-center py-5">
                    <div class="alert alert-danger" role="alert">
                        <i class="fas fa-exclamation-triangle me-2"></i>
                        Произошла ошибка при поиске туров. Пожалуйста, попробуйте позже.
                    </div>
                    <button class="btn btn-primary mt-3" onclick="window.location.reload()">
                        <i class="fas fa-sync-alt me-2"></i>Попробовать снова
                    </button>
                </div>
            `;
        }
    }
}

/**
 * Форматирует дату в строку формата YYYY-MM-DD
 */
function formatDate(date) {
    const day = String(date.getDate()).padStart(2, '0');
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const year = date.getFullYear();
    return `${year}-${month}-${day}`;
}
