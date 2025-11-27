document.addEventListener('DOMContentLoaded', () => {
    const header = document.querySelector('.header-container');
    if (!header) return;

    const applyHeaderShape = () => {
        const atTop = window.scrollY <= 8;
        header.classList.toggle('is-rolling', !atTop);
    };

    window.addEventListener('scroll', applyHeaderShape, { passive: true });
    applyHeaderShape();
});
