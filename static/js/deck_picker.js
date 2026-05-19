function deckPickerInit(options) {
  const searchUrl = options.searchUrl;
  const resultsContainer = document.querySelector(options.resultsContainer);
  const selectedContainer = document.querySelector(options.selectedCardsContainer);
  const hiddenField = document.querySelector(options.hiddenField);
  const searchInput = document.querySelector('#card-search-query');

  let selectedCards = Array.isArray(options.initialData) ? options.initialData : [];

  function saveSelectedCards() {
    hiddenField.value = JSON.stringify(selectedCards.map((item) => ({
      card_id: item.card_id,
      quantity: item.quantity,
    })));
  }

  function renderSelectedCards() {
    selectedContainer.innerHTML = '';

    if (selectedCards.length === 0) {
      selectedContainer.innerHTML = '<p class="empty-state">No cards selected yet.</p>';
      saveSelectedCards();
      return;
    }

    selectedCards.forEach((card) => {
      const row = document.createElement('div');
      row.className = 'selected-card';
      row.innerHTML = `
        <div class="selected-card-main">
          <strong>${card.quantity}×</strong>
          <span class="selected-card-name">${card.name}</span>
          <span class="selected-card-type">${card.type_line || ''}</span>
        </div>
        <div class="selected-card-controls">
          <button type="button" class="qty-btn" data-action="decrease" data-card-id="${card.card_id}">-</button>
          <button type="button" class="qty-btn" data-action="increase" data-card-id="${card.card_id}">+</button>
          <button type="button" class="remove-card" data-card-id="${card.card_id}">Remove</button>
        </div>
      `;
      selectedContainer.appendChild(row);
    });

    saveSelectedCards();
  }

  function updateCardQuantity(cardId, delta) {
    const index = selectedCards.findIndex((entry) => entry.card_id === cardId);
    if (index === -1) {
      return;
    }
    const item = selectedCards[index];
    item.quantity = Math.max(1, item.quantity + delta);
    renderSelectedCards();
  }

  function removeSelectedCard(cardId) {
    selectedCards = selectedCards.filter((entry) => entry.card_id !== cardId);
    renderSelectedCards();
  }

  function addSelectedCard(cardData) {
    const existing = selectedCards.find((entry) => entry.card_id === cardData.card_id);
    if (existing) {
      existing.quantity += 1;
    } else {
      selectedCards.push({
        card_id: cardData.card_id,
        quantity: 1,
        name: cardData.name,
        type_line: cardData.type_line,
      });
    }
    renderSelectedCards();
  }

  function escapeHtml(value) {
    return String(value)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');
  }

  function renderSearchResults(cards) {
    resultsContainer.innerHTML = '';
    if (!cards.length) {
      resultsContainer.innerHTML = '<p class="empty-state">No cards found.</p>';
      return;
    }

    cards.forEach((card) => {
      const row = document.createElement('div');
      row.className = 'card-result';

      const imageLink = document.createElement('a');
      imageLink.className = 'card-result-image-link';
      imageLink.target = '_blank';
      imageLink.rel = 'noopener noreferrer';
      imageLink.href = card.oracle_id ? `/cards/${card.oracle_id}/` : '#';

      let image;
      if (card.image_url) {
        image = document.createElement('img');
        image.src = card.image_url;
        image.alt = `${card.name}`;
      } else {
        image = document.createElement('div');
        image.textContent = 'No image';
        image.style.padding = '2rem';
        image.style.textAlign = 'center';
        image.style.color = '#c7c7d1';
      }
      image.className = 'card-result-image';
      imageLink.appendChild(image);

      const info = document.createElement('div');
      info.className = 'card-result-info';

      const nameLink = document.createElement('a');
      nameLink.href = card.oracle_id ? `/cards/${card.oracle_id}/` : '#';
      nameLink.target = '_blank';
      nameLink.rel = 'noopener noreferrer';
      nameLink.textContent = card.name;
      nameLink.className = 'card-result-name';

      const meta = document.createElement('div');
      meta.className = 'card-result-meta';
      meta.textContent = card.type_line || '';

      const rules = document.createElement('p');
      rules.className = 'card-result-text';
      rules.textContent = card.oracle_text || '';

      const cost = document.createElement('div');
      cost.className = 'card-result-cost';
      cost.textContent = card.mana_cost || '';

      info.appendChild(nameLink);
      info.appendChild(cost);
      info.appendChild(meta);
      info.appendChild(rules);

      const button = document.createElement('button');
      button.type = 'button';
      button.className = 'add-card';
      button.dataset.cardId = card.card_id;
      button.textContent = 'Add';
      button.addEventListener('click', function () {
        addSelectedCard(card);
      });

      row.appendChild(imageLink);
      row.appendChild(info);
      row.appendChild(button);
      resultsContainer.appendChild(row);
    });
  }

  function fetchCardResults(query) {
    if (!query.trim()) {
      resultsContainer.innerHTML = '<p class="empty-state">Type to search cards.</p>';
      return;
    }
    fetch(`${searchUrl}?q=${encodeURIComponent(query)}`)
      .then((response) => response.json())
      .then((data) => {
        renderSearchResults(data.results || []);
      })
      .catch(() => {
        resultsContainer.innerHTML = '<p class="empty-state">Unable to fetch cards. Try again.</p>';
      });
  }

  searchInput.addEventListener('input', function () {
    fetchCardResults(this.value);
  });

  selectedContainer.addEventListener('click', function (event) {
    const button = event.target.closest('button');
    if (!button) return;
    const cardId = Number(button.dataset.cardId);
    if (button.dataset.action === 'increase') {
      updateCardQuantity(cardId, 1);
    }
    if (button.dataset.action === 'decrease') {
      updateCardQuantity(cardId, -1);
    }
    if (button.classList.contains('remove-card')) {
      removeSelectedCard(cardId);
    }
  });

  renderSelectedCards();
}
