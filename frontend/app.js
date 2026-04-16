// Inicializar Lienzo
const canvas = new fabric.Canvas('editor-canvas', {
    width: 800,
    height: 600,
    preserveObjectStacking: true // Mantiene el Z-Index estricto
});

const loader = document.getElementById('loader');
const layersList = document.getElementById('layers-list');

// Escuchadores de herramientas de texto
const textTools = document.getElementById('text-tools');
const noSelection = document.getElementById('no-selection');
const textInput = document.getElementById('text-input');
const textColor = document.getElementById('text-color');
const textSize = document.getElementById('text-size');

// Actualizar panel al seleccionar objetos
canvas.on('selection:created', handleSelection);
canvas.on('selection:updated', handleSelection);
canvas.on('selection:cleared', () => {
    textTools.classList.add('hidden');
    noSelection.classList.remove('hidden');
});

// Actualizar lista de capas cuando cambian los objetos
canvas.on('object:added', renderLayers);
canvas.on('object:removed', renderLayers);
canvas.on('object:modified', renderLayers);

function handleSelection(e) {
    const obj = e.selected[0];
    if (obj && obj.type === 'i-text') {
        textTools.classList.remove('hidden');
        noSelection.classList.add('hidden');
        textInput.value = obj.text;
        textColor.value = obj.fill;
        textSize.value = obj.fontSize;
    } else {
        textTools.classList.add('hidden');
        noSelection.classList.remove('hidden');
    }
}

// Vinculación bidireccional UI -> Canvas
textInput.addEventListener('input', (e) => {
    const obj = canvas.getActiveObject();
    if (obj && obj.type === 'i-text') { obj.set('text', e.target.value); canvas.renderAll(); }
});
textColor.addEventListener('input', (e) => {
    const obj = canvas.getActiveObject();
    if (obj && obj.type === 'i-text') { obj.set('fill', e.target.value); canvas.renderAll(); }
});
textSize.addEventListener('input', (e) => {
    const obj = canvas.getActiveObject();
    if (obj && obj.type === 'i-text') { obj.set('fontSize', parseInt(e.target.value)); canvas.renderAll(); }
});

let selectionRect;
let isSelecting = false;

document.getElementById('btn-select-area').onclick = () => {
    isSelecting = !isSelecting;
    const btn = document.getElementById('btn-select-area');
    if (isSelecting) {
        btn.innerText = "Dibujando... (Click para procesar)";
        btn.classList.add('bg-red-600');
        canvas.defaultCursor = 'crosshair';
        
        selectionRect = new fabric.Rect({
            fill: 'rgba(255,0,0,0.3)',
            stroke: 'red',
            strokeWidth: 2,
            selectable: false,
            left: 0, top: 0, width: 0, height: 0
        });
        canvas.add(selectionRect);

        canvas.on('mouse:down', startSelection);
        canvas.on('mouse:move', updateSelection);
        canvas.on('mouse:up', () => {});
    } else {
        processWithROI();
    }
};

function startSelection(o) {
    const pointer = canvas.getPointer(o.e);
    selectionRect.set({ left: pointer.x, top: pointer.y, width: 0, height: 0 });
}

function updateSelection(o) {
    if (!selectionRect.canvas) return;
    const pointer = canvas.getPointer(o.e);
    selectionRect.set({
        width: Math.abs(pointer.x - selectionRect.left),
        height: Math.abs(pointer.y - selectionRect.top)
    });
    canvas.renderAll();
}

async function processWithROI() {
    const btn = document.getElementById('btn-select-area');
    btn.innerText = "Seleccionar Área";
    btn.classList.remove('bg-red-600');
    canvas.defaultCursor = 'default';
    
    const roi = {
        x: selectionRect.left, y: selectionRect.top,
        w: selectionRect.width, h: selectionRect.height
    };
    
    canvas.remove(selectionRect);
    canvas.off('mouse:down');
    canvas.off('mouse:move');
    
    // Necesitamos el archivo original. Lo pediremos si no hay imagen base.
    document.getElementById('uploadImage').click();
    window.pendingROI = roi;
}

// Actualizar el listener de uploadImage para manejar ROI
document.getElementById('uploadImage').addEventListener('change', async function(e) {
    const file = e.target.files[0];
    if (!file) return;

    loader.classList.remove('hidden');
    
    const formData = new FormData();
    formData.append('file', file);
    if (window.pendingROI) {
        formData.append('roi', JSON.stringify(window.pendingROI));
        window.pendingROI = null;
    }

    canvas.clear();

    try {
        const res = await fetch('/api/decompose', { method: 'POST', body: formData });
        const data = await res.json();

        if(data.error) {
            alert("Error procesando: " + data.error);
            loader.classList.add('hidden');
            return;
        }

        // 1. Fondo Reconstruido (Inpainted) -> Capa Base (Index 0)
        fabric.Image.fromURL('data:image/png;base64,' + data.base_background, function(bg) {
            bg.set({ left: 0, top: 0, selectable: false, evented: false, name: "Fondo Base (IA)" });
            
            // Ajustar tamaño del canvas a la imagen
            canvas.setWidth(bg.width);
            canvas.setHeight(bg.height);
            canvas.add(bg);
            bg.sendToBack();

            // 2. Insertar Objetos Extraídos
            data.objects.forEach((o, index) => {
                fabric.Image.fromURL('data:image/png;base64,' + o.img, function(imgObj) {
                    imgObj.set({ left: o.x, top: o.y, name: `Objeto ${index + 1}` });
                    canvas.add(imgObj);
                });
            });

            // 3. Insertar Textos como Textos editables interactivos
            data.texts.forEach((t, index) => {
                const textObj = new fabric.IText(t.text, {
                    left: t.x, top: t.y, fontSize: t.size || 20, fontFamily: t.font, fill: t.color, name: `Texto: ${t.text.substring(0,10)}`
                });
                canvas.add(textObj);
            });
            
        });
    } catch (error) {
        console.error("Error AI Engine:", error);
    } finally {
        loader.classList.add('hidden');
    }
});

// Añadir imágenes nuevas sobre las existentes sin alterar fondo
document.getElementById('addLayerImage').addEventListener('change', function(e) {
    const file = e.target.files[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = function(f) {
        const data = f.target.result;
        fabric.Image.fromURL(data, function(img) {
            img.set({ left: 50, top: 50, name: `Importado: ${file.name}` });
            canvas.add(img);
            canvas.setActiveObject(img);
        });
    };
    reader.readAsDataURL(file);
});

// Gestor de Renderizado de Capas en Panel Lateral
function renderLayers() {
    layersList.innerHTML = '';
    const objects = canvas.getObjects();
    // Invertir para que el superior se vea arriba en la lista
    for (let i = objects.length - 1; i >= 0; i--) {
        const obj = objects[i];
        const li = document.createElement('li');
        li.className = 'layer-item bg-gray-900 border border-gray-700 rounded p-2 text-sm flex justify-between items-center';
        li.innerHTML = `
            <span class="truncate w-3/4">${obj.name || obj.type} (Capa ${i + 1})</span>
            <div class="flex gap-2">
                <button title="Traer al frente" class="text-gray-400 hover:text-white" onclick="bringForward(${i})">↑</button>
                <button title="Enviar atrás" class="text-gray-400 hover:text-white" onclick="sendBackward(${i})">↓</button>
                <button title="Eliminar" class="text-red-500 hover:text-red-400 font-bold" onclick="removeLayer(${i})">X</button>
            </div>
        `;
        // Seleccionar en el lienzo al clickear la capa
        li.onclick = (e) => {
            if(e.target.tagName !== 'BUTTON') canvas.setActiveObject(obj);
        };
        layersList.appendChild(li);
    }
}

// Funciones de control de Z-Index
window.bringForward = function(index) {
    const obj = canvas.item(index);
    if(obj) { canvas.bringForward(obj); canvas.renderAll(); renderLayers(); }
};
window.sendBackward = function(index) {
    const obj = canvas.item(index);
    // Evitar que envíen detrás de la capa base inpaint
    if(obj && index > 1) { canvas.sendBackwards(obj); canvas.renderAll(); renderLayers(); }
};
window.removeLayer = function(index) {
    const obj = canvas.item(index);
    if(obj) { canvas.remove(obj); canvas.renderAll(); renderLayers(); }
};
