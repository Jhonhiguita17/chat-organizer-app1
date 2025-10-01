<?php
// Ruta al archivo JSON generado por Python
$ruta_json = __DIR__ . '/data/datos_organizados.json';

// Leer y decodificar JSON
$datos = [];
if (file_exists($ruta_json)) {
    $json = file_get_contents($ruta_json);
    $datos = json_decode($json, true);
} else {
    die("Archivo JSON no encontrado. Ejecuta primero el script Python para generarlo.");
}

// Obtener filtro por autor desde URL (ejemplo: ?autor=Yesid Cortes)
$autor = isset($_GET['autor']) ? trim(strtolower($_GET['autor'])) : null;

// Filtrar mensajes por autor si se especifica
$filtrados = [];
if ($autor) {
    foreach ($datos as $mensaje) {
        if (isset($mensaje['autor']) && strtolower($mensaje['autor']) === $autor) {
            $filtrados[] = $mensaje;
        }
    }
} else {
    // Si no hay filtro, mostrar primeros 20 mensajes
    $filtrados = array_slice($datos, 0, 20);
}
?>

<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Mensajes organizados</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .mensaje { border-bottom: 1px solid #ccc; padding: 10px 0; }
        .fecha { color: #555; font-size: 0.9em; }
        .autor { font-weight: bold; }
        .subestacion { font-style: italic; color: #007BFF; }
        .codigo { color: #d9534f; }
        .filtro { margin-bottom: 20px; }
        input[type="text"] { padding: 5px; width: 250px; }
        input[type="submit"] { padding: 5px 10px; }
    </style>
</head>
<body>

<h1>Mensajes organizados</h1>

<div class="filtro">
    <form method="get" action="">
        <label for="autor">Filtrar por autor:</label>
        <input type="text" id="autor" name="autor" value="<?php echo htmlspecialchars($autor ?? ''); ?>" placeholder="Ejemplo: Yesid Cortes">
        <input type="submit" value="Filtrar">
        <?php if ($autor): ?>
            <a href="index.php" style="margin-left:10px;">Mostrar todos</a>
        <?php endif; ?>
    </form>
</div>

<?php if (count($filtrados) === 0): ?>
    <p>No se encontraron mensajes para el filtro especificado.</p>
<?php else: ?>
    <?php foreach ($filtrados as $m): ?>
        <div class="mensaje">
            <div class="fecha"><?php echo htmlspecialchars($m['fecha_hora']); ?></div>
            <div class="autor"><?php echo htmlspecialchars($m['autor']); ?></div>
            <?php if (!empty($m['subestacion'])): ?>
                <div class="subestacion">Subestación: <?php echo htmlspecialchars($m['subestacion']); ?></div>
            <?php endif; ?>
            <?php if (!empty($m['incidentes'])): ?>
                <div class="codigo">Incidentes: <?php echo htmlspecialchars(implode(', ', $m['incidentes'])); ?></div>
            <?php endif; ?>
            <?php if (!empty($m['requerimientos'])): ?>
                <div class="codigo">Requerimientos: <?php echo htmlspecialchars(implode(', ', $m['requerimientos'])); ?></div>
            <?php endif; ?>
            <p><?php echo nl2br(htmlspecialchars($m['mensaje'])); ?></p>
        </div>
    <?php endforeach; ?>
<?php endif; ?>

</body>
</html>
