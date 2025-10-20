document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("tts-form");
    const speakBtn = document.getElementById("speak-btn");
    const fairytaleBtn = document.getElementById("fairytale-btn");
    const textArea = document.getElementById("tts-text");

    if (form && speakBtn) {
        form.addEventListener("submit", function () {
            speakBtn.disabled = true;
            speakBtn.textContent = "Generuji…";
        });
    }

    if (fairytaleBtn && textArea) {
        fairytaleBtn.onclick = async function(e) {
            e.preventDefault();
            fairytaleBtn.disabled = true;
            fairytaleBtn.textContent = "Generuji…";
            try {
                const resp = await fetch("/fairytale");
                if (!resp.ok) throw new Error(await resp.text());
                const text = await resp.text();
                textArea.value = text;
                textArea.focus();
                if (speakBtn) speakBtn.focus();
            } catch (err) {
                alert("Chyba při generování pohádky: " + err.message);
            } finally {
                fairytaleBtn.disabled = false;
                fairytaleBtn.textContent = "Generovat pohádku";
            }
        };
    }
});
