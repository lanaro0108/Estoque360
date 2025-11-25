document.addEventListener('DOMContentLoaded', () => {
    const navLinks = document.querySelectorAll('.nav-links a');
    const heroImage = document.querySelector('.hero-image'); // O elemento escuro

    // Função que detecta colisão entre dois elementos
    function checkOverlap() {
        if (!heroImage) return;

        // Pega o retângulo (posição) da imagem escura
        const darkRect = heroImage.getBoundingClientRect();

        navLinks.forEach(link => {
            // Pega o retângulo do link atual
            const linkRect = link.getBoundingClientRect();

            // Matemática de colisão (verifica se os retângulos se tocam)
            // Se NÃO estiver fora, então está dentro (sobrepondo)
            const isOverlapping = !(
                linkRect.right < darkRect.left ||
                linkRect.left > darkRect.right ||
                linkRect.bottom < darkRect.top ||
                linkRect.top > darkRect.bottom
            );

            // Adiciona ou remove a classe baseada na sobreposição
            if (isOverlapping) {
                link.classList.add('on-dark');
            } else {
                link.classList.remove('on-dark');
            }
        });
    }

    // Otimização: Roda a função no scroll e no redimensionar da tela
    window.addEventListener('scroll', checkOverlap, { passive: true });
    window.addEventListener('resize', checkOverlap, { passive: true });

    // Roda uma vez ao carregar para garantir o estado inicial
    checkOverlap();
});