// Invoke Functions Call on Document Loaded
//document.addEventListener('DOMContentLoaded', function () {
//  hljs.highlightAll();
//});


var alertWrapper = document.querySelector('.alert')
var alertClose = document.querySelector('.alert__close')

var vinay = document.querySelector('vinay')

if (alertWrapper) {
  vinay.addEventListener('X', () =>
    alertWrapper.style.display = 'none'
  )
}
