// carrito.js - intercepta formularios relacionados al carrito y realiza POST por fetch
(function(){
    function getCSRFToken() {
        const el = document.querySelector('input[name=csrfmiddlewaretoken]');
        return el ? el.value : '';
    }

    async function postAction(form, extra){
        const action = form.dataset.action || form.querySelector('input[name=action]')?.value || (extra && extra.action);
        const formData = new FormData(form);
        if (extra) {
            for (const k in extra) formData.set(k, extra[k]);
        }
        // include CSRF if not present
        if (!formData.has('csrfmiddlewaretoken')) {
            const token = getCSRFToken();
            if (token) formData.set('csrfmiddlewaretoken', token);
        }

        // Always post cart actions to the products handler
        const resp = await fetch('/productos/', {
            method: 'POST',
            body: formData,
        });

        if (!resp.ok) return;

        // actualizar fragmento del carrito desde /productos/
        const listResp = await fetch('/productos/');
        if (!listResp.ok) return;
        const text = await listResp.text();
        // parsear y extraer el contenedor .cart
        const parser = new DOMParser();
        const doc = parser.parseFromString(text, 'text/html');
        const newCart = doc.querySelector('#cart-container');
        if (newCart) {
            const current = document.querySelector('#cart-container');
            if (current) current.innerHTML = newCart.innerHTML;
        }
    }

    function init(){
        // interceptar formularios con class cart-action (pagar) y los forms dentro de .cart y tarjetas
        document.addEventListener('submit', function(e){
            const form = e.target;
            // solo manejar si tiene input[name=action] o class cart-action
            if (form.classList && form.classList.contains('cart-action')) {
                e.preventDefault();
                postAction(form);
                return;
            }

            const actionInput = form.querySelector && form.querySelector('input[name=action]');
            if (actionInput) {
                const actionVal = actionInput.value;
                // actions we want to handle via JS: add, remove, set
                if (['add','remove','set'].includes(actionVal)) {
                    e.preventDefault();
                    postAction(form);
                }
            }
        }, true);
    }

    document.addEventListener('DOMContentLoaded', init);
})();
