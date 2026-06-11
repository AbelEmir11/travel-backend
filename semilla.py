import json
from datetime import date, datetime
from app import app, db
from models import Alojamiento, Actividad, Servicio, Usuario, Reserva
from werkzeug.security import generate_password_hash

# Datos completos de los alojamientos en Argentina
ALOJAMIENTOS_SEMILLA = [
  {
    "id": "mendoza-cavas-wine",
    "title": "Cavas Wine Lodge",
    "location": "Mendoza",
    "province": "Mendoza",
    "price": 20,
    "rating": 4.95,
    "reviewsCount": 142,
    "images": [
      "https://theluxtraveller.com/wp-content/uploads/2014/01/Cavas-Wine-Lodge-Mendoza.jpg",
      "https://images.unsplash.com/photo-1560493676-04071c5f467b?q=80&w=800&auto=format&fit=crop",
      "https://images.unsplash.com/photo-1510812431401-41d2bd2722f3?q=80&w=800&auto=format&fit=crop",
      "https://www.chandon.com.ar/wp-content/uploads/2024/01/MG_0859.jpg",
    ],
    "type": "all_inclusive",
    "experienceLabel": "All Inclusive Premium",
    "description": "Ubicado entre viñedos a los pies de la imponente Cordillera de los Andes, Cavas Wine Lodge ofrece una experiencia de inmersión total en la cultura del vino de Mendoza. Bungalows privados con piscina propia, terrazas con fogones y vistas infinitas.",
    "activities": [
      "Visita guiada y cata privada en bodegas de renombre",
      "Trekking al amanecer con vista al Cordón del Plata",
      "Clase de cocina criolla y maridaje con Malbec",
      "Tratamiento de vinoterapia en el spa privado"
    ],
    "amenities": [
      "Cava subterránea",
      "Piscina privada por bungalow",
      "Fogón en terraza",
      "Restaurante de autor",
      "Wifi de fibra óptica"
    ],
    "featured": True
  },
  {
    "id": "bariloche-llao-llao",
    "title": "Llao Llao Resort & Golf",
    "location": "Bariloche",
    "province": "Río Negro",
    "price": 70,
    "rating": 4.89,
    "reviewsCount": 312,
    "images": [
      "https://latam.beyondba.com/wp-content/uploads/2023/06/dsc9493-scaled.jpg",
      "https://images.blacktomato.com/2016/08/Llao-Llao-8.jpg?auto=compress%2Cformat&fit=scale&h=1203&ixlib=php-3.3.0&w=2048&s=c53679b52962f581235ed7bb7d73d38b",
      "https://www.fivestaralliance.com/files/fivestaralliance.com/field/image/nodes/2009/10533/10533_0_llaollaohotelandresort_fsa-g.jpg",
      "https://www.emporiumtravel.de/files/content/royal-hideaways/ferne_laender/argentinien/llao-llao-hotel-resort-golf-spa/llao-llao-hotel-resort-golf-spa-3.jpg",
      "https://st3.idealista.pt/news/arquivos/styles/fullwidth_xl/public/2012-12/127.jpg?VersionId=ce1IYgselK3qWzhL9c6Y587uYmKgdtiI&itok=jzlXNtcD"
      
    ],
    "type": "estadia",
    "experienceLabel": "Solo Estadía de Lujo",
    "description": "Un ícono de la Patagonia argentina. Rodeado de los lagos Nahuel Huapi y Moreno, y custodiado por los cerros López y Capilla. Cuenta con un imponente campo de golf de 18 hoyos, spa de primer nivel y la calidez clásica de la madera patagónica.",
    "activities": [
      "Navegación privada por el Lago Nahuel Huapi",
      "Trekking guiado al Cerro Llao Llao",
      "Degustación guiada de chocolates artesanales y cervezas locales",
      "Green fee en el campo de golf de campeonato"
    ],
    "amenities": [
      "Campo de golf de 18 hoyos",
      "Spa & Health Club",
      "Piscina in/out climatizada",
      "Té Llao Llao en salón histórico",
      "Puerto propio"
    ],
    "featured": True
  },
  {
    "id": "iguazu-gran-melia",
    "title": "Gran Meliá Iguazú",
    "location": "Iguazú",
    "province": "Misiones",
    "price": 35,
    "rating": 4.87,
    "reviewsCount": 228,
    "images": [
      "https://3.bp.blogspot.com/-KQaAzpxB4v8/VFl2eKV8QII/AAAAAAAAEsQ/BeuEO65Y3w4CiHgLbK3FBQAsiSaSOrk4QCPcB/s1600/imagen-aerea-cataratas-del-iguazu.jpg",
      " https://th.bing.com/th/id/R.003f7c0cf08357e71ab6fe2158892363?rik=uWBLp%2f%2fkdHMFdQ&pid=ImgRaw&r=0",
      "https://images.squarespace-cdn.com/content/v1/5856bc666a49634cd55b0ba9/0dbe1767-5d0b-48a9-8e86-48cae9f7142a/iguazu-falls.jpeg ",
      "https://wallpapercave.com/wp/WjQ8rcA.jpg",
      "https://et-website.s3.amazonaws.com/uploads/2018/08/Enchanting-Travels-Iguazu-Falls-Argentina-Tours-1.jpg"

    ],
    "type": "viaje",
    "experienceLabel": "Viaje con Aventura",
    "description": "El único hotel ubicado dentro del Parque Nacional Iguazú, con vistas directas a la Garganta del Diablo. Despertate con el rugido de las cataratas y observá la fauna exótica desde tu balcón privado en medio de la selva misionera.",
    "activities": [
      "Paseo de luna llena a las Cataratas del Iguazú",
      "Aventura náutica bajo los saltos en gomón rígido",
      "Safari fotográfico por el corazón de la selva misionera",
      "Senderismo de avistaje de aves y fauna nativa"
    ],
    "amenities": [
      "Piscina infinity de 50 metros con vista al río",
      "Acceso directo a las pasarelas del parque",
      "Rooftop bar con vista a las cataratas",
      "Spa orgánico con tratamientos locales",
      "Gimnasio 24/7"
    ],
    "featured": True
  },
  {
    "id": "calafate-eolo",
    "title": "Eolo - Patagonia's Spirit",
    "location": "Patagonia",
    "province": "Santa Cruz",
    "price": 30,
    "rating": 4.97,
    "reviewsCount": 98,
    "images": [
      "https://www.elcalafateya.com/wp-content/uploads/2019/03/camaras-vivo-calafate-santa-cruz-argentina-e1551725687400.jpg",
      "https://gopatagonic.com/wp-content/uploads/2024/11/52648405035_3533b73fce_o.jpg",
      "https://tolkeyenpatagonia.com/wp-content/uploads/2019/01/glaciar-sur-pioneros-1.jpg",
      "https://blog.moebiusviajes.com/wp-content/uploads/2020/12/LOS-10-MEJORES-HOTELES-EN-EL-CALAFATE-EN-2020-altocalafate-946x568-6-768x461.jpg",
      "https://unaideaunviaje.com/wp-content/uploads/2015/05/calafate-perito-moreno-unaideaunviaje-10.jpg"
    ],
    "type": "all_inclusive",
    "experienceLabel": "All Inclusive Explorer",
    "description": "Eolo encarna el espíritu de la Patagonia profunda. Ubicado en un valle de 4.000 hectáreas camino al Glaciar Perito Moreno, este lodge boutique ofrece un silencio absoluto, vistas panorámicas sobrecogedoras y un nivel de confort inigualable.",
    "activities": [
      "Caminata con grampones sobre el Glaciar Perito Moreno",
      "Navegación frente a las paredes de hielo del glaciar",
      "Cabalgatas guiadas por el Cerro Frías",
      "Observación astronómica del cielo patagónico"
    ],
    "amenities": [
      "Guías expertos residentes",
      "Gastronomía de cordero patagónico y trucha",
      "Biblioteca con vistas panorámicas",
      "Piscina cubierta climatizada",
      "Telescopio profesional"
    ],
    "featured": False
  },
  {
    "id": "bsas-faena",
    "title": "Faena Hotel Buenos Aires",
    "location": "Buenos Aires",
    "province": "CABA",
    "price": 80,
    "rating": 4.79,
    "reviewsCount": 415,
    "images": [
      "https://media.istockphoto.com/id/534164779/photo/faena-hotel-at-puerto-madero-buenos-aires-argentina.jpg?s=170667a&w=0&k=20&c=_Q1kqWVX--qr9aUmHz08jVWeelyOEivYnKHsZfvnYlc=",
      "https://www.myboutiquehotel.com/photos/5640/faena-hotel-buenos-aires-buenos-aires-034-84178-1110x700.jpg",
      "https://th.bing.com/th/id/R.19b2e04409327390a9ebad587b37dcb8?rik=sxslNkL9yzb7Fw&riu=http%3a%2f%2fmedia.architecturaldigest.com%2fphotos%2f582de0290058935c3e94c0a4%2fmaster%2fpass%2ffaena-buenos-aires-02.jpg&ehk=cgnmpIDW9MKltVMacoZk6fkElGFt%2fNR7QxYkb5P%2fSUE%3d&risl=&pid=ImgRaw&r=0",
      "https://static.prod.r53.tablethotels.com/media/hotels/slideshow_images_staged/large/1098191.jpg",
      "https://faena.buenosaireshotelsargentina.com/data/Pictures/OriginalPhoto/2800/280059/280059753/buenos-aires-faena-hotel-picture-38.JPEG"
    ],
    "type": "estadia",
    "experienceLabel": "Solo Estadía / Arte",
    "description": "Diseñado por Philippe Starck, el Faena Hotel es un epicentro de arte, drama y lujo en el exclusivo barrio de Puerto Madero. Con su icónica piscina del corona de cristal y su estilo cabaret, redefine la experiencia urbana porteña.",
    "activities": [
      "Entradas VIP al aclamado show 'Rojo Tango'",
      "Tour privado de arte por San Telmo y La Boca",
      "Ruta gastronómica y cata de carnes en la mejor parrilla de la ciudad",
      "Clase privada de tango en el salón de los espejos"
    ],
    "amenities": [
      "Piscina icónica con bar y corona",
      "Teatro y cabaret privado",
      "Bistro con cocina porteña moderna",
      "Hammam y spa holístico",
      "Servicio de Experience Manager"
    ],
    "featured": False
  },
  {
    "id": "mendoza-casa-de-uco",
    "title": "Las Leñas Ski Resort",
    "location": "Las Leñas, Malargüe",
    "province": "Mendoza",
    "price": 40,
    "rating": 4.91,
    "reviewsCount": 118,
    "images": [
      "https://th.bing.com/th/id/R.1afc1eb518a9b4b4260015866992af3e?rik=dSmmhVOvm3R5yw&pid=ImgRaw&r=0",
      "https://th.bing.com/th/id/R.021ca39f76a0e378686f7db95685cf51?rik=BqRcd5Dry2FDmQ&pid=ImgRaw&r=0",
      "https://laslenas.com/wp-content/uploads/2023/06/nota3-1.jpg",
      "https://tse1.mm.bing.net/th/id/OIP.V_Qa6rEIBC1mu-XTnGhZ9AHaD8?r=0&rs=1&pid=ImgDetMain&o=7&rm=3",
      "https://images.travelclass.tur.br/uploads/2018/09/restaurantes-valle-nevado.jpg"
    ],
    "type": "viaje",
    "experienceLabel": "Viaje con Nieve",
    "description":"Las Leñas es el principal centro de esquí de Argentina, ubicado en el corazón de la cordillera de los Andes. Con una de las temporadas más largas de Sudamérica y una infraestructura de primer nivel, ofrece pistas para todos los niveles, desde principiantes hasta expertos. Además de esquí y snowboard, Las Leñas cuenta con una amplia variedad de actividades para disfrutar al máximo de la montaña.",
    "activities": [
      "Esquí y snowboard",
      "Ascenso al Cerro Chapelco en telesilla panorámica",
      "Trekking guiado por senderos patagónicos",
      "Clase de arquería y paseos en bicicleta por el valle"
    ],
    "amenities": [
      "Pistas de esquí de nivel internacional",
      "Escuela de esquí con instructores certificados",
      "Alquiler de equipos de esquí y snowboard",
      "Bicicletas de montaña gratuitas",
      "Sector de fuegos exterior"
    ],
    "featured": False
  },
  {
    "id": "cordoba-estancia-el-colibri",
    "title": "Estancia El Colibrí",
    "location": "Córdoba",
    "province": "Córdoba",
    "price": 30,
    "rating": 4.90,
    "reviewsCount": 86,
    "images": [
      "https://www.estanciaelcolibri.com/wp-content/uploads/2025/02/facade-cordoba-2.png",
      "https://www.estanciaelcolibri.com/wp-content/uploads/2025/02/facade-drone-argentine-1.png",
      "https://tse4.mm.bing.net/th/id/OIP.stuKaD-Eff7S_OZjLL_bGgHaE8?r=0&rs=1&pid=ImgDetMain&o=7&rm=3",
      "https://www.qietut.com/wp-content/uploads/2021/11/qietut-estancia-el-colibri-experiences-horseriding-family.jpg",
      "https://www.estanciaelcolibri.com/cdn-cgi/image/quality=70,format=auto,onerror=redirect,metadata=none/wp-content/uploads/2025/02/H-oa-20ans-.png"
    ],
    "type": "all_inclusive",
    "experienceLabel": "All Inclusive Estancia",
    "description": "Inspirada en las antiguas estancias argentinas del siglo XIX, El Colibrí invita a descubrir la esencia de la vida de campo en Córdoba. Paseos a caballo, polo de nivel internacional y alta gastronomía elaborada con ingredientes frescos de su propia huerta orgánica.",
    "activities": [
      "Cabalgata guiada por las sierras de Córdoba",
      "Clase introductoria al polo y práctica en picadero",
      "Tarde de campo con asado criollo de cinco pasos",
      "Cosecha en la huerta y clase de empanadas tradicionales"
    ],
    "amenities": [
      "Club de polo y caballerizas",
      "Huerta orgánica y granja",
      "Piscina exterior templada",
      "Spa y sauna seco",
      "Restaurante Farm-to-Table"
    ],
    "featured": False
  },
  {
    "id": "neuquen-correntoso",
    "title": "Correntoso Lake & River Hotel",
    "location": "Neuquén",
    "province": "Neuquén",
    "price": 37,
    "rating": 4.93,
    "reviewsCount": 154,
    "images": [
      "https://turismo-en-argentina.com/wp-content/uploads/2023/02/Turismo-en-Neuquen-1024x439.jpg",
      "https://www.interpatagonia.com/plantillas/grandes/34096-01Gr.jpg",
      "https://tse4.mm.bing.net/th/id/OIP.5dBGGw29WJVB77EXoL_iHAHaHa?r=0&pid=ImgDet&w=474&h=474&rs=1&o=7&rm=3",
      "https://d1x2jsuj9gaph.cloudfront.net/imageRepo/6/0/101/998/155/13_P.jpg",
      "https://www.interpatagonia.com/plantillas/grandes/17487-07Gr.jpg"
    ],
    "type": "estadia",
    "experienceLabel": "Solo Estadía Premium",
    "description": "Ubicado en Villa La Angostura, justo en la desembocadura del río Correntoso en el lago Nahuel Huapi. Un hotel histórico con vistas majestuosas, ideal para amantes de la pesca con mosca, el relax de montaña y el senderismo patagónico.",
    "activities": [
      "Pesca con mosca guiada en la boca del Río Correntoso",
      "Kayak y paddle surf en el lago Nahuel Huapi",
      "Trekking guiado al mirador Belvedere y cascada Inacayal",
      "Cata de vinos patagónicos frente al lago al atardecer"
    ],
    "amenities": [
      "Spa con circuito hídrico completo",
      "Piscina in/out climatizada frente al lago",
      "Puerto de embarque propio",
      "Té de la tarde estilo Correntoso",
      "Cava de vinos locales"
    ],
    "featured": False
  },
  {
    "id": "salta-colome",
    "title": "Estancia Colomé",
    "location": "Salta",
    "province": "Salta",
    "price": 20,
    "rating": 4.96,
    "reviewsCount": 78,
    "images": [
      "https://www.amerian.com/wp-content/uploads/2025/09/03B_Banner_958x574_3a1729a2-26af-45e7-8626-30c91015b84d.jpg",
      "https://www.welcomeargentina.com/paseos/museo-james-turrell/museo-james-turrell-a.jpg",
      "https://images.adsttc.com/media/images/5d27/a094/284d/d1c1/d200/014a/slideshow/james_turrell_guggenheim_01.jpg?1562878083",
      "https://www.estilodv.com/public/images/guia/3444-bodega-colome.jpg",
      "https://i.pinimg.com/originals/a3/8e/3a/a38e3ae464c85b5aa943bf085fd9ced5.jpg"
    ],
    "type": "viaje",
    "experienceLabel": "Viaje de Altura",
    "description": "Ubicada en los Valles Calchaquíes a 2.300 metros de altura. Combina la bodega activa más antigua de Argentina con un exclusivo hotel boutique y el alucinante Museo James Turrell, un espacio único en el mundo dedicado a la luz.",
    "activities": [
      "Visita privada al Museo de Luz James Turrell",
      "Cata dirigida de vinos biodinámicos de altura extrema",
      "Caminata entre viñedos centenarios con vistas panorámicas",
      "Observación guiada del firmamento salteño en noche estrellada"
    ],
    "amenities": [
      "Museo de arte contemporáneo James Turrell",
      "Bodega biodinámica y viñedos",
      "Restaurante de cocina andina de autor",
      "Piscina exterior panorámica",
      "Sala de lectura con chimenea"
    ],
    "featured": False
  }
]

def cargar_semillas():
    print("[INFO] Recreando la base de datos (drop_all y create_all)...")
    db.drop_all()
    db.create_all()
    
    print("[INFO] Insertando usuarios de prueba...")
    usuarios = [
        Usuario(nombre="Juan Cliente", email="cliente@travel.com", password_hash=generate_password_hash("cliente123"), rol="cliente"),
        Usuario(nombre="Maria Comercial", email="comercial@travel.com", password_hash=generate_password_hash("comercial123"), rol="comercial"),
        Usuario(nombre="Carlos General", email="general@travel.com", password_hash=generate_password_hash("general123"), rol="general")
    ]
    for u in usuarios:
        db.session.add(u)
    db.session.commit()
    
    print("[INFO] Insertando alojamientos, actividades y servicios...")
    for data in ALOJAMIENTOS_SEMILLA:
        desc = 0
        act = True
        if data["id"] == "bariloche-llao-llao":
            desc = 25
        elif data["id"] == "iguazu-gran-melia":
            desc = 10
        elif data["id"] == "mendoza-casa-de-uco":
            act = False

        aloj = Alojamiento(
            id=data["id"],
            titulo=data["title"],
            ubicacion=data["location"],
            provincia=data["province"],
            precio=data["price"],
            calificacion=data["rating"],
            reviews_count=data["reviewsCount"],
            tipo=data["type"],
            experience_label=data["experienceLabel"],
            descripcion=data["description"],
            destacado=data["featured"],
            activo=act,
            descuento=desc
        )
        # Usamos el setter para convertir lista a JSON string
        aloj.imagenes = data["images"]
        
        db.session.add(aloj)
        db.session.flush() # Obtiene el ID para relaciones si fuera numérico
        
        # Cargar actividades asociadas
        for act_desc in data["activities"]:
            actividad = Actividad(alojamiento_id=aloj.id, descripcion=act_desc)
            db.session.add(actividad)
            
        # Cargar servicios asociados
        for srv_name in data["amenities"]:
            servicio = Servicio(alojamiento_id=aloj.id, nombre=srv_name)
            db.session.add(servicio)
            
    # Obtener el usuario 'Juan Cliente' (ID = 1 ya que se limpió e insertó al inicio)
    usuario_cliente = Usuario.query.filter_by(email="cliente@travel.com").first()
    
    if usuario_cliente:
        print("[INFO] Insertando reservas de prueba para estadísticas...")
        reservas_prueba = [
            # Reservas de Mayo 2026 (Mes anterior)
            Reserva(
                usuario_id=usuario_cliente.id,
                alojamiento_id="mendoza-cavas-wine",
                check_in=date(2026, 5, 10),
                check_out=date(2026, 5, 13),
                huespedes=2,
                notes="Luna de miel en Mendoza.",
                precio_total=1480,
                estado="confirmed",
                fecha_creacion=datetime(2026, 5, 1, 12, 0)
            ),
            Reserva(
                usuario_id=usuario_cliente.id,
                alojamiento_id="bariloche-llao-llao",
                check_in=date(2026, 5, 18),
                check_out=date(2026, 5, 22),
                huespedes=2,
                notes="Estadía clásica de golf.",
                precio_total=1208,
                estado="confirmed",
                fecha_creacion=datetime(2026, 5, 12, 10, 30)
            ),
            Reserva(
                usuario_id=usuario_cliente.id,
                alojamiento_id="iguazu-gran-melia",
                check_in=date(2026, 5, 25),
                check_out=date(2026, 5, 27),
                huespedes=3,
                notes="Escapada familiar de aventura.",
                precio_total=670,
                estado="confirmed",
                fecha_creacion=datetime(2026, 5, 20, 15, 45)
            ),
            # Reservas de Junio 2026 (Mes actual)
            Reserva(
                usuario_id=usuario_cliente.id,
                alojamiento_id="calafate-eolo",
                check_in=date(2026, 6, 2),
                check_out=date(2026, 6, 7),
                huespedes=2,
                notes="Expedición a los glaciares.",
                precio_total=2640,
                estado="confirmed",
                fecha_creacion=datetime(2026, 5, 28, 9, 15)
            ),
            Reserva(
                usuario_id=usuario_cliente.id,
                alojamiento_id="cordoba-estancia-el-colibri",
                check_in=date(2026, 6, 12),
                check_out=date(2026, 6, 15),
                huespedes=2,
                notes="Fin de semana largo de campo.",
                precio_total=1060,
                estado="pending",
                fecha_creacion=datetime(2026, 6, 1, 14, 0)
            ),
            Reserva(
                usuario_id=usuario_cliente.id,
                alojamiento_id="salta-colome",
                check_in=date(2026, 6, 20),
                check_out=date(2026, 6, 24),
                huespedes=2,
                notes="Visita al museo James Turrell y cata.",
                precio_total=1720,
                estado="confirmed",
                fecha_creacion=datetime(2026, 6, 5, 11, 20)
            )
        ]
        
        for r in reservas_prueba:
            db.session.add(r)
            
    db.session.commit()
    print("[OK] Base de datos populada con exito!")

if __name__ == "__main__":
    with app.app_context():
        cargar_semillas()
