/**
 * Utilidades comunes para los mapas del sistema (MapLibre GL JS).
 * Estilo base: OpenFreeMap "liberty" — vector tiles gratuitos basados en
 * OpenStreetMap, sin necesidad de API key, con un acabado visual similar
 * al de Google Maps (calles, edificios, nombres de lugares).
 */

const ESTILO_MAPA = "https://tiles.openfreemap.org/styles/liberty";
const CENTRO_BOLIVIA = [-65.0, -16.5]; // [lng, lat] - MapLibre usa lng primero

/** Crea un mapa MapLibre centrado en Bolivia por defecto. */
function crearMapa(contenedorId, opciones = {}) {
    const mapa = new maplibregl.Map({
        container: contenedorId,
        style: ESTILO_MAPA,
        center: opciones.center || CENTRO_BOLIVIA,
        zoom: opciones.zoom !== undefined ? opciones.zoom : 5.5,
    });
    mapa.addControl(new maplibregl.NavigationControl(), "top-right");
    return mapa;
}

/**
 * Geocodifica un nombre de lugar usando Nominatim (OpenStreetMap) y
 * devuelve {lat, lng, nombre} del primer resultado, o null si no encontró nada.
 * Se acota la búsqueda a Bolivia para mejorar la precisión de resultados.
 */
async function geocodificar(texto) {
    const url = "https://nominatim.openstreetmap.org/search?format=json&limit=1&countrycodes=bo&q=" + encodeURIComponent(texto);
    const resp = await fetch(url, { headers: { "Accept-Language": "es" } });
    if (!resp.ok) throw new Error("No se pudo consultar el geocodificador.");
    const data = await resp.json();
    if (!data.length) return null;
    return {
        lat: parseFloat(data[0].lat),
        lng: parseFloat(data[0].lon),
        nombre: data[0].display_name,
    };
}

/**
 * Calcula la ruta real por carretera entre dos puntos usando el servicio
 * público de OSRM (Open Source Routing Machine, basado en OpenStreetMap).
 * Devuelve { puntos: [[lat,lng],...], distanciaKm, duracionMin }.
 */
async function calcularRutaPorCarretera(origen, destino) {
    const coords = `${origen.lng},${origen.lat};${destino.lng},${destino.lat}`;
    const url = `https://router.project-osrm.org/route/v1/driving/${coords}?overview=full&geometries=geojson`;
    const resp = await fetch(url);
    if (!resp.ok) throw new Error("No se pudo calcular la ruta por carretera.");
    const data = await resp.json();
    if (data.code !== "Ok" || !data.routes || !data.routes.length) {
        throw new Error("OSRM no encontró una ruta por carretera entre esos puntos.");
    }
    const ruta = data.routes[0];
    // OSRM devuelve [lng, lat]; el sistema guarda [lat, lng] internamente.
    const puntos = ruta.geometry.coordinates.map(([lng, lat]) => [lat, lng]);
    return {
        puntos: puntos,
        distanciaKm: ruta.distance / 1000,
        duracionMin: ruta.duration / 60,
    };
}

/** Construye un GeoJSON de tipo LineString a partir de una lista de puntos [lat,lng]. */
function puntosALineString(puntos) {
    return {
        type: "Feature",
        geometry: {
            type: "LineString",
            coordinates: puntos.map(([lat, lng]) => [lng, lat]), // MapLibre usa [lng, lat]
        },
    };
}

/** Calcula el bounding box [[minLng,minLat],[maxLng,maxLat]] de una lista de puntos [lat,lng]. */
function calcularBounds(puntos) {
    let minLat = Infinity, maxLat = -Infinity, minLng = Infinity, maxLng = -Infinity;
    puntos.forEach(([lat, lng]) => {
        if (lat < minLat) minLat = lat;
        if (lat > maxLat) maxLat = lat;
        if (lng < minLng) minLng = lng;
        if (lng > maxLng) maxLng = lng;
    });
    return [[minLng, minLat], [maxLng, maxLat]];
}
