import json
from app import app, db
from models import Alojamiento, Actividad, Servicio

# Datos completos de los alojamientos en Argentina
ALOJAMIENTOS_SEMILLA = [
  {
    "id": "mendoza-cavas-wine",
    "title": "Cavas Wine Lodge",
    "location": "Mendoza",
    "province": "Mendoza",
    "price": 480,
    "rating": 4.95,
    "reviewsCount": 142,
    "images": [
      "https://th.bing.com/th/id/R.a808fd675ac69265ac047796d4c589ee?rik=S%2fjFHGR%2b6F90Qw&pid=ImgRaw&r=0",
      "https://picsum.photos/seed/cavas2/800/600",
      "https://picsum.photos/seed/cavas3/800/600"
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
    "price": 390,
    "rating": 4.89,
    "reviewsCount": 312,
    "images": [
      "https://picsum.photos/seed/llao1/800/600",
      "https://picsum.photos/seed/llao2/800/600",
      "https://picsum.photos/seed/llao3/800/600"
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
    "price": 350,
    "rating": 4.87,
    "reviewsCount": 228,
    "images": [
      "https://picsum.photos/seed/melia1/800/600",
      "https://picsum.photos/seed/melia2/800/600",
      "https://picsum.photos/seed/melia3/800/600"
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
    "price": 520,
    "rating": 4.97,
    "reviewsCount": 98,
    "images": [
      "https://picsum.photos/seed/eolo1/800/600",
      "https://picsum.photos/seed/eolo2/800/600",
      "https://picsum.photos/seed/eolo3/800/600"
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
    "price": 280,
    "rating": 4.79,
    "reviewsCount": 415,
    "images": [
      "https://picsum.photos/seed/faena1/800/600",
      "https://picsum.photos/seed/faena2/800/600",
      "https://picsum.photos/seed/faena3/800/600"
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
    "title": "Casa de Uco Vineyards & Wine Resort",
    "location": "Mendoza",
    "province": "Mendoza",
    "price": 410,
    "rating": 4.91,
    "reviewsCount": 118,
    "images": [
      "https://picsum.photos/seed/uco1/800/600",
      "https://picsum.photos/seed/uco2/800/600",
      "https://picsum.photos/seed/uco3/800/600"
    ],
    "type": "viaje",
    "experienceLabel": "Viaje Enológico",
    "description": "Situado en el corazón del Valle de Uco, rodeado de viñedos y de la imponente cordillera. Un hotel de diseño minimalista y concreto que flota sobre una laguna privada. Ofrece una inmersión directa en la elaboración de tu propio vino.",
    "activities": [
      "Cosecha y taller de blending de vino propio",
      "Trekking de alta montaña en Manzano Histórico",
      "Cabalgata entre viñedos con asado criollo al aire libre",
      "Clase de arquería y paseos en bicicleta por el valle"
    ],
    "amenities": [
      "Laguna privada",
      "Bodega de última generación",
      "Spa con tratamientos de agua mineral propia",
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
    "price": 340,
    "rating": 4.90,
    "reviewsCount": 86,
    "images": [
      "https://picsum.photos/seed/colibri1/800/600",
      "https://picsum.photos/seed/colibri2/800/600",
      "https://picsum.photos/seed/colibri3/800/600"
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
    "price": 370,
    "rating": 4.93,
    "reviewsCount": 154,
    "images": [
      "https://picsum.photos/seed/correntoso1/800/600",
      "https://picsum.photos/seed/correntoso2/800/600",
      "https://picsum.photos/seed/correntoso3/800/600"
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
    "price": 420,
    "rating": 4.96,
    "reviewsCount": 78,
    "images": [
      "https://picsum.photos/seed/colome1/800/600",
      "https://picsum.photos/seed/colome2/800/600",
      "https://picsum.photos/seed/colome3/800/600"
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
    print("[INFO] Vaciando tablas existentes...")
    # Eliminar datos para evitar duplicados en la base de datos
    db.session.query(Actividad).delete()
    db.session.query(Servicio).delete()
    db.session.query(Alojamiento).delete()
    db.session.commit()
    
    print("[INFO] Insertando alojamientos, actividades y servicios...")
    for data in ALOJAMIENTOS_SEMILLA:
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
            destacado=data["featured"]
        )
        # Usamos el setter para convertir lista a JSON string
        aloj.imagenes = data["images"]
        
        db.session.add(aloj)
        db.session.flush() # Obtiene el ID para relaciones si fuera numérico (aquí es string, pero es buena práctica)
        
        # Cargar actividades asociadas
        for act_desc in data["activities"]:
            actividad = Actividad(alojamiento_id=aloj.id, descripcion=act_desc)
            db.session.add(actividad)
            
        # Cargar servicios asociados
        for srv_name in data["amenities"]:
            servicio = Servicio(alojamiento_id=aloj.id, nombre=srv_name)
            db.session.add(servicio)
            
    db.session.commit()
    print("[OK] Base de datos populada con exito!")

if __name__ == "__main__":
    with app.app_context():
        cargar_semillas()
