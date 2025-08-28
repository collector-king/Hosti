document.getElementById('upload-form').addEventListener('submit', function(e) {
    const fileInput = document.getElementById('python-file');
    const file = fileInput.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = function(event) {
            document.getElementById('code-output').textContent = event.target.result;
        };
        reader.readAsText(file);
    }
});
