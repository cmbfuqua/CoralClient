function filterItems() {
    const filterValue = document.getElementById('subtype_filter').value;
    const items = document.querySelectorAll('.specimen-card');

    items.forEach(item => {
        const itemSubtype = item.getAttribute('data-item_subtype');
        if (filterValue === 'all' || itemSubtype === filterValue) {
            item.style.display = '';
        } else {
            item.style.display = 'none';
        }
    });
}
