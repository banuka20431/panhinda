document.addEventListener('DOMContentLoaded', function () {

    document.querySelectorAll('.flash-close').forEach(function (btn) {
    
        btn.addEventListener('click', function () {

            this.parentElement.style.display = 'none';
            
        });
    
    });

});