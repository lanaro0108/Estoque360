document.addEventListener('DOMContentLoaded', () => {
    const target = document.getElementById('typewriter-text');
    const cursor = document.querySelector('.typewriter-cursor');
    if (!target || !cursor) return;

    // Texto e pausas: ajuste "pauseAfter" (ms) para controlar quanto tempo
    // cada frase fica parada antes de começar a apagar.
    //
    // IMPORTANTE:
    // - use número em eraseTo (ex: 0, 5, 10) ou
    // - use 'algum texto'.length para apagar até o tamanho desse texto.
    const steps = [
        // 1) Digita tudo, depois apaga até ficar "Somos um"
        { text: 'Somos um gerenciador de estoque', eraseTo: 'Somos '.length, pauseAfter: 1200 },

        // 2) Corrige "um" -> "o", apagando até "Somos " (com espaço)
        { text: 'Somos O gerenciador de estoque', eraseTo: 'Somos '.length, pauseAfter: 400 },

        // 3) Mostra a marca, NÃO apaga nada (usa length para pular a deleção)
        { text: 'Somos o Estoque360', eraseTo: 'Somos o Estoque360'.length, pauseAfter: 850 },

        // 4) Versão final com ponto dramático, aí apaga tudo
        { text: 'Somos o Estoque360°', eraseTo: 0, pauseAfter: 4500 },
    ];

    // Velocidade de digitar (ms por letra)
    const typeSpeed = 52;
    // Velocidade de apagar (ms por letra)
    const eraseSpeed = 12;

    let stepIndex = 0;
    let charIndex = 0;
    let erasing = false;

    // Converte eraseTo (número ou string) para um número alvo (índice)
    const getEraseTarget = (eraseTo) => {
        if (typeof eraseTo === 'number') return eraseTo;
        if (typeof eraseTo === 'string') return eraseTo.length;
        return 0;
    };

    const tick = () => {
        const { text, eraseTo, pauseAfter } = steps[stepIndex];
        const eraseTarget = getEraseTarget(eraseTo);

        if (!erasing) {
            // Fase de digitar
            target.textContent = text.slice(0, charIndex + 1);
            charIndex += 1;

            if (charIndex === text.length) {
                // Chegou no fim da frase: começa a fase de apagar depois da pausa
                erasing = true;
                setTimeout(tick, pauseAfter);
                return;
            }

            setTimeout(tick, typeSpeed);
        } else {
            // Fase de apagar

            // Se eraseTarget for igual ao tamanho da frase,
            // não apaga nada (serve para passos que só acrescentam)
            if (eraseTarget === text.length) {
                erasing = false;
                stepIndex = (stepIndex + 1) % steps.length;
                setTimeout(tick, 0);
                return;
            }

            target.textContent = text.slice(0, charIndex - 1);
            charIndex -= 1;

            // Parar de apagar quando chegar no índice definido em eraseTo
            if (charIndex === eraseTarget) {
                erasing = false;
                stepIndex = (stepIndex + 1) % steps.length;
                setTimeout(tick, 250);
                return;
            }

            setTimeout(tick, eraseSpeed);
        }
    };

    tick();

    // Typewriter do título principal (roda apenas uma vez)
    const titleTarget = document.getElementById('title-typewriter-text');
    const titleCursor = titleTarget ? titleTarget.nextElementSibling : null;
    if (titleTarget && titleCursor) {
        // Frase única
        const titleText = 'A automação está na moda.';
        // Ajuste a velocidade de digitação do título (ms por letra)
        const titleTypeSpeed = 90;
        let titleIndex = 0;

        const typeTitle = () => {
            // Digita letra por letra
            titleTarget.textContent = titleText.slice(0, titleIndex + 1);
            titleIndex += 1;

            if (titleIndex === titleText.length) {
                // Esconde o cursor quando terminar
                titleCursor.style.visibility = 'hidden';
                return;
            }

            setTimeout(typeTitle, titleTypeSpeed);
        };

        typeTitle();
    }
    const pricingTarget = document.getElementById('pricing-typewriter-text');
    const pricingCursor = pricingTarget ? pricingTarget.nextElementSibling : null;

    if (pricingTarget && pricingCursor) {
        const pricingText = 'Escolha o plano ideal para você.';
        const pricingSpeed = 50; // Velocidade em ms (pode ajustar)
        let pricingIndex = 0;

        const typePricing = () => {
            pricingTarget.textContent = pricingText.slice(0, pricingIndex + 1);
            pricingIndex += 1;

            if (pricingIndex === pricingText.length) {
                pricingCursor.style.visibility = 'hidden'; // Esconde cursor no final
                return;
            }

            setTimeout(typePricing, pricingSpeed);
        };

        const observer = new IntersectionObserver((entries) => {
            if (entries[0].isIntersecting) {
                typePricing();
                observer.disconnect(); // Para de observar depois que rodou
            }
        });
        observer.observe(pricingTarget);
    }
});