async function checkGrammar() {
    const text = document.getElementById("inputText").value;

    if (!text.trim()) {
        alert("Please enter a sentence.");
        return;
    }

    const response = await fetch("http://127.0.0.1:8000/check-grammar", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ text: text })
    });

    const data = await response.json();

    document.getElementById("correctedText").innerText = data.corrected_text;
    document.getElementById("explanation").innerText = data.explanation;
}
