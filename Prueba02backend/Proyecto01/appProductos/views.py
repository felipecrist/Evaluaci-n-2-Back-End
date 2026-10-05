from django.shortcuts import render, redirect
from appUsuarios.models import Usuario
from .models import Producto, Noticia


def _usuario_actual(request):
    usuario_sesion = request.session.get('usuario')
    if not usuario_sesion:
        return None
    try:
        return Usuario.objects.get(usuario=usuario_sesion)
    except Usuario.DoesNotExist:
        return None


def _es_admin(request):
    usuario = _usuario_actual(request)
    return bool(usuario and usuario.admin)


def _seed_productos_y_noticias():
    if not Producto.objects.exists():
        Producto.objects.bulk_create([
            Producto(id='p1', nombre='Auriculares inalámbricos Pro', detalle='Audio inmersivo', descripcion='Auriculares con cancelación de ruido', precio=129.0, imagen='/static/images/product1.jpg', stock=10),
            Producto(id='p2', nombre='Smartphone Z Ultra', detalle='Cámara avanzada', descripcion='Smartphone tope de gama', precio=999.0, imagen='/static/images/product2.jpg', stock=5),
            Producto(id='p3', nombre='Reloj Fit 5', detalle='Seguimiento de salud', descripcion='Smartwatch con sensores avanzados', precio=199.0, imagen='/static/images/product3.jpg', stock=8),
            Producto(id='p4', nombre='Altavoz Bluetooth Max', detalle='Bajo potente', descripcion='Altavoz portátil con batería larga', precio=89.0, imagen='/static/images/product4.jpg', stock=12),
        ])

    if not Noticia.objects.exists():
        Noticia.objects.bulk_create([
            Noticia(id='n1', titulo='IA integrada en smartphones de nueva generación', fecha='04 Sep 2026', extracto='Los fabricantes presentan chips con aceleración de IA que mejoran la fotografía y la batería.', imagen='/static/images/news1.jpg'),
            Noticia(id='n2', titulo='Smartwatches con sensores avanzados de salud', fecha='28 Ago 2026', extracto='Nuevos modelos añaden monitorización continua y mejores algoritmos de detección.', imagen='/static/images/news2.jpg'),
            Noticia(id='n3', titulo='Conectividad 6G: ¿qué esperar?', fecha='15 Ago 2026', extracto='Investigaciones muestran latencias ultra-bajas para aplicaciones inmersivas.', imagen='/static/images/news3.jpg'),
        ])


def home(request):
    _seed_productos_y_noticias()
    usuario_actual = _usuario_actual(request)
    return render(request, "index.html", {'usuario': usuario_actual})


def productos(request):
    _seed_productos_y_noticias()
    carrito = request.session.get('carrito', {})

    if request.method == 'POST':
        action = request.POST.get('action')
        pid = request.POST.get('id_producto')
        usuario_sesion = request.session.get('usuario')
        es_admin = _es_admin(request)

        if action == 'add':
            if not usuario_sesion:
                request.session['aviso_login'] = 'Debes iniciar sesión para agregar productos al carrito.'
                return redirect('/cuenta/')
            producto = Producto.objects.filter(id=pid).first()
            if not producto:
                return redirect('/productos/')
            try:
                cantidad = int(request.POST.get('cantidad', '1'))
            except ValueError:
                cantidad = 1
            if cantidad < 1:
                cantidad = 1
            current_in_cart = carrito.get(pid, 0)
            if current_in_cart + cantidad > producto.stock:
                request.session['aviso_stock'] = f"No hay suficiente stock para {producto.nombre}. Disponible: {producto.stock - current_in_cart}"
                return redirect('/productos/')
            carrito[pid] = current_in_cart + cantidad
        elif action == 'remove':
            if pid in carrito:
                carrito[pid] = carrito.get(pid, 0) - 1
                if carrito[pid] <= 0:
                    carrito.pop(pid, None)
        elif action == 'set':
            try:
                qty = int(request.POST.get('quantity', '0'))
            except ValueError:
                qty = 0
            if qty > 0:
                carrito[pid] = qty
            else:
                carrito.pop(pid, None)
        elif action == 'delete_producto' and es_admin:
            producto = Producto.objects.filter(id=pid).first()
            if producto:
                producto.eliminado = True
                producto.save()
        elif action == 'reponer_stock' and es_admin:
            producto = Producto.objects.filter(id=pid).first()
            if producto:
                try:
                    nueva = int(request.POST.get('cantidad_stock', '0'))
                except ValueError:
                    nueva = 0
                if nueva >= 0:
                    producto.stock = nueva
                    producto.save()
            return redirect('/productos/')
        elif action == 'pagar':
            if not usuario_sesion:
                request.session['aviso_login'] = 'Debes iniciar sesión para completar la compra.'
                return redirect('/cuenta/')
            for pidc, qty in carrito.items():
                producto = Producto.objects.filter(id=pidc).first()
                if producto is None:
                    continue
                if producto.stock < qty:
                    request.session['aviso_stock'] = f"Stock insuficiente para {producto.nombre}. Disponible: {producto.stock}"
                    return redirect('/productos/')
            comprador = Usuario.objects.filter(usuario=usuario_sesion).first()
            for pidc, qty in list(carrito.items()):
                producto = Producto.objects.filter(id=pidc).first()
                if producto is None:
                    continue
                producto.stock = producto.stock - qty
                producto.save()
                if comprador is not None:
                    historial = list(comprador.historial or [])
                    historial.append(f"{qty} x {producto.nombre}")
                    comprador.historial = historial
                    comprador.save()
            request.session['carrito'] = {}
            request.session['aviso_compra'] = 'Compra exitosa'
            return redirect('/productos/')

        request.session['carrito'] = carrito
        return redirect('/productos/')

    usuario_sesion = request.session.get('usuario')
    es_admin = _es_admin(request)
    productos_list = []
    for producto in Producto.objects.all().order_by('nombre'):
        if producto.eliminado and not es_admin:
            continue
        productos_list.append({
            'id': producto.id,
            'nombre': producto.nombre,
            'detalle': producto.detalle,
            'descripcion': producto.descripcion,
            'precio': float(producto.precio),
            'imagen': producto.imagen,
            'eliminado': producto.eliminado,
            'stock': producto.stock,
            'cantidad_en_carrito': carrito.get(producto.id, 0),
        })

    total = sum(float(item['precio']) * item['cantidad_en_carrito'] for item in productos_list)
    aviso_compra = request.session.pop('aviso_compra', '')
    aviso_stock = request.session.pop('aviso_stock', '')

    carrito_visible = {}
    for pid, qty in carrito.items():
        producto = Producto.objects.filter(id=pid).first()
        if not producto:
            continue
        if producto.eliminado and not es_admin:
            continue
        carrito_visible[pid] = qty

    usuario_actual = _usuario_actual(request)
    return render(request, "productos.html", {
        "productos": productos_list,
        'carrito': carrito_visible,
        'total': total,
        'es_admin': es_admin,
        'aviso_compra': aviso_compra,
        'aviso_stock': aviso_stock,
        'usuario': usuario_actual,
    })


def noticias(request):
    _seed_productos_y_noticias()
    usuario_sesion = request.session.get('usuario')
    es_admin = _es_admin(request)

    if request.method == 'POST':
        action = request.POST.get('action')
        nid = request.POST.get('id_noticia')
        if action == 'delete_noticia' and es_admin:
            noticia = Noticia.objects.filter(id=nid).first()
            if noticia:
                noticia.eliminado = True
                noticia.save()
        return redirect('/noticias/')

    noticias_list = []
    for noticia in Noticia.objects.all().order_by('id'):
        if noticia.eliminado and not es_admin:
            continue
        noticias_list.append({
            'id': noticia.id,
            'titulo': noticia.titulo,
            'fecha': noticia.fecha,
            'extracto': noticia.extracto,
            'imagen': noticia.imagen,
            'eliminado': noticia.eliminado,
        })

    usuario_actual = _usuario_actual(request)
    return render(request, "noticias.html", {'noticias': noticias_list, 'es_admin': es_admin, 'usuario': usuario_actual})


def contacto(request):
    usuario_actual = _usuario_actual(request)
    return render(request, "contacto.html", {'usuario': usuario_actual})


def producto_detalle(request, pid):
    _seed_productos_y_noticias()
    carrito = request.session.get('carrito', {})
    es_admin = _es_admin(request)
    producto = Producto.objects.filter(id=pid).first()
    if not producto:
        return redirect('/productos/')

    productos_list = []
    for item in Producto.objects.all().order_by('nombre'):
        if item.eliminado and not es_admin:
            continue
        productos_list.append({
            'id': item.id,
            'nombre': item.nombre,
            'detalle': item.detalle,
            'descripcion': item.descripcion,
            'precio': float(item.precio),
            'imagen': item.imagen,
            'eliminado': item.eliminado,
            'stock': item.stock,
            'cantidad_en_carrito': carrito.get(item.id, 0),
        })

    carrito_visible = {}
    for pidc, qty in carrito.items():
        prodc = Producto.objects.filter(id=pidc).first()
        if not prodc:
            continue
        if prodc.eliminado and not es_admin:
            continue
        carrito_visible[pidc] = qty

    total = sum(float(Producto.objects.filter(id=p).first().precio) * qty for p, qty in carrito_visible.items() if Producto.objects.filter(id=p).first())
    usuario_actual = _usuario_actual(request)
    aviso_compra = request.session.pop('aviso_compra', '')
    aviso_stock = request.session.pop('aviso_stock', '')

    return render(request, "listadeproductos/producto_detalle.html", {
        'producto': {
            'id': producto.id,
            'nombre': producto.nombre,
            'detalle': producto.detalle,
            'descripcion': producto.descripcion,
            'precio': float(producto.precio),
            'imagen': producto.imagen,
            'eliminado': producto.eliminado,
            'stock': producto.stock,
        },
        'productos': productos_list,
        'carrito': carrito_visible,
        'total': total,
        'es_admin': es_admin,
        'usuario': usuario_actual,
        'aviso_compra': aviso_compra,
        'aviso_stock': aviso_stock,
    })