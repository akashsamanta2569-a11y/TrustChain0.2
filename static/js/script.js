function copyHash() {
    const hashText = document.getElementById("hashValue").innerText;
    navigator.clipboard.writeText(hashText).then(() => {
        const btn = document.getElementById("copyBtn");
        btn.innerText = "Copied! ✅";
        setTimeout(() => { btn.innerText = "Copy Hash"; }, 2000);
    });
}