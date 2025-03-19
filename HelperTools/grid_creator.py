import pivy.coin as coin

def createGrid(obj, grid_material):
    """Generate an XY plane grid with red X-axis and green Y-axis, using the grid color from the property view."""
    grid_node = coin.SoSeparator()  # Main container for the grid

    # === GRID FACE (for one-sided rendering) ===
    coords = coin.SoCoordinate3()
    faceSet = coin.SoIndexedFaceSet()

    # Define materials for the X and Y axes
    materialRed = coin.SoMaterial()
    materialRed.diffuseColor = coin.SbColor(1, 0, 0)  # Red for X-axis

    materialGreen = coin.SoMaterial()
    materialGreen.diffuseColor = coin.SbColor(0, 1, 0)  # Green for Y-axis

    size = obj.Size
    spacing = obj.Spacing
    half_size = size // 2  # Keep grid centered

    print(f"Creating grid: Size = {size}, Spacing = {spacing}, Grid Color = {obj.Color}")

    # === GRID LINES ===
    grid_coords = coin.SoCoordinate3()
    grid_lines = coin.SoIndexedLineSet()
    points = []
    indices = []

    for y in range(-half_size, half_size + spacing, spacing):
        start_index = len(points)
        points.append(coin.SbVec3f(-half_size, y, 0))  # Left
        points.append(coin.SbVec3f(half_size, y, 0))   # Right
        indices.extend([start_index, start_index + 1, -1])  # -1 ends each line

    for x in range(-half_size, half_size + spacing, spacing):
        start_index = len(points)
        points.append(coin.SbVec3f(x, -half_size, 0))  # Bottom
        points.append(coin.SbVec3f(x, half_size, 0))   # Top
        indices.extend([start_index, start_index + 1, -1])  # -1 ends each line

    grid_coords.point.setValues(0, len(points), points)
    grid_lines.coordIndex.setValues(0, len(indices), indices)

    # === GRID NODE ===
    gridSeparator = coin.SoSeparator()
    gridSeparator.addChild(grid_material)
    gridSeparator.addChild(grid_coords)
    gridSeparator.addChild(grid_lines)
    gridSeparator.addChild(faceSet)

    # === X-AXIS ===
    x_axis_coords = coin.SoCoordinate3()
    x_axis_coords.point.setValues(0, 2, [
        coin.SbVec3f(-half_size, 0, 0),
        coin.SbVec3f(half_size, 0, 0)
    ])
    x_axis_lines = coin.SoIndexedLineSet()
    x_axis_lines.coordIndex.setValues(0, 3, [0, 1, -1])

    x_axis_style = coin.SoDrawStyle()
    x_axis_style.lineWidth = 2  # Slightly thicker X-axis

    x_axis_node = coin.SoSeparator()
    x_axis_node.addChild(x_axis_style)  # Apply line width
    x_axis_node.addChild(materialRed)
    x_axis_node.addChild(x_axis_coords)
    x_axis_node.addChild(x_axis_lines)

    # === Y-AXIS ===
    y_axis_coords = coin.SoCoordinate3()
    y_axis_coords.point.setValues(0, 2, [
        coin.SbVec3f(0, -half_size, 0),
        coin.SbVec3f(0, half_size, 0)
    ])
    y_axis_lines = coin.SoIndexedLineSet()
    y_axis_lines.coordIndex.setValues(0, 3, [0, 1, -1])

    y_axis_style = coin.SoDrawStyle()
    y_axis_style.lineWidth = 2  # Slightly thicker Y-axis

    y_axis_node = coin.SoSeparator()
    y_axis_node.addChild(y_axis_style)  # Apply line width
    y_axis_node.addChild(materialGreen)
    y_axis_node.addChild(y_axis_coords)
    y_axis_node.addChild(y_axis_lines)

    # === ENSURE X & Y AXES ARE DRAWN LAST BUT RESPECT DEPTH ===
    grid_node.addChild(gridSeparator)  # Add the grid first
    grid_node.addChild(x_axis_node)    # Add the X-axis second
    grid_node.addChild(y_axis_node)    # Add the Y-axis last

    return grid_node