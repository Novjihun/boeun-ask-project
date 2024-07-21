<script>
document.querySelectorAll('.upload_hidden').forEach(input => {
  input.addEventListener('change', function() {
    const fileBox = this.closest('.file_box');
    const fileNameInput = fileBox.querySelector('.upload_name');
    const deleteButton = fileBox.querySelector('.btn_file_del');

    if (this.files.length > 0) {
      fileNameInput.value = this.files[0].name;
      deleteButton.style.display = 'block'; // 삭제 버튼 표시
    } else {
      fileNameInput.value = '';
      deleteButton.style.display = 'none'; // 삭제 버튼 숨김
    }
  });
});

document.querySelectorAll('.btn_file_del').forEach(button => {
  button.addEventListener('click', function() {
    const fileBox = this.closest('.file_box');
    const fileInput = fileBox.querySelector('.upload_hidden');
    const fileNameInput = fileBox.querySelector('.upload_name');

    fileInput.value = '';
    fileNameInput.value = '';
    this.style.display = 'none'; // 삭제 버튼 숨김
  });
});
</script>
