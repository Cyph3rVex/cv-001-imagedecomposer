// --- SISTEMA DE INTEGRIDAD PÚBLICA ---
const appContainer = document.getElementById('app-container');

// El motor ya no requiere login manual, pero el backend limita por IP
window.logout = function() {
    window.location.reload();
}

// --- NÚCLEO DEL EDITOR ---
const canvas = new fabric.Canvas('editor-canvas', {
    width: 800,
    height: 600,
    preserveObjectStacking: true
});

const loader = document.getElementById('loader');
const layersList = document.getElementById('layers-list');
const textTools = document.getElementById('text-tools');
const noSelection = document.getElementById('no-selection');
const textInput = document.getElementById('text-input');
const textColor = document.getElementById('text-color');
const textSize = document.getElementById('text-size');

canvas.on('selection:created', handleSelection);
canvas.on('selection:updated', handleSelection);
canvas.on('selection:cleared', () => {
    textTools.classList.add('hidden');
    noSelection.classList.remove('hidden');
});
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
        btn.innerText = "[ DIBUJANDO ROI ]";
        btn.classList.add('bg-[#00ffcc]', 'text-black');
        canvas.defaultCursor = 'crosshair';
        
        selectionRect = new fabric.Rect({
            fill: 'rgba(0,255,204,0.2)', stroke: '#00ffcc', strokeWidth: 2,
            selectable: false, left: 0, top: 0, width: 0, height: 0
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
    btn.innerText = "SELECCIONAR ÁREA";
    btn.classList.remove('bg-[#00ffcc]', 'text-black');
    canvas.defaultCursor = 'default';
    
    const roi = {
        x: selectionRect.left, y: selectionRect.top,
        w: selectionRect.width, h: selectionRect.height
    };
    
    canvas.remove(selectionRect);
    canvas.off('mouse:down');
    canvas.off('mouse:move');
    
    document.getElementById('uploadImage').click();
    window.pendingROI = roi;
}

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
        const token = sessionStorage.getItem('cv_token');
        if(!token) { logout(); return; }

        const res = await fetch('/api/decompose', { 
            method: 'POST', 
            headers: { 'Authorization': `Bearer ${token}` }, // INYECCIÓN DE TOKEN SECRETO
            body: formData 
        });
        
        if(res.status === 401) { logout(); throw new Error('Token expirado'); }
        const data = await res.json();

        if(data.error) {
            alert("Error del motor IA: " + data.error);
            loader.classList.add('hidden');
            return;
        }

        fabric.Image.fromURL('data:image/png;base64,' + data.base_background, function(bg) {
            bg.set({ left: 0, top: 0, selectable: false, evented: false, name: "BASE (IA Inpaint)" });
            canvas.setWidth(bg.width);
            canvas.setHeight(bg.height);
            canvas.add(bg);
            bg.sendToBack();

            data.objects.forEach((o, index) => {
                fabric.Image.fromURL('data:image/png;base64,' + o.img, function(imgObj) {
                    imgObj.set({ left: o.x, top: o.y, name: `OBJ_${index + 1}` });
                    canvas.add(imgObj);
                });
            });

            data.texts.forEach((t, index) => {
                const textObj = new fabric.IText(t.text, {
                    left: t.x, top: t.y, fontSize: t.size || 20, fontFamily: t.font, fill: t.color, name: `TXT_${t.text.substring(0,6)}`
                });
                canvas.add(textObj);
            });
            
        });
    } catch (error) {
        console.error("Seguridad/Red:", error);
    } finally {
        loader.classList.add('hidden');
    }
});

document.getElementById('addLayerImage').addEventListener('change', function(e) {
    const file = e.target.files[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = function(f) {
        const data = f.target.result;
        fabric.Image.fromURL(data, function(img) {
            img.set({ left: 50, top: 50, name: `EXT_${file.name.substring(0,5)}` });
            canvas.add(img);
            canvas.setActiveObject(img);
        });
    };
    reader.readAsDataURL(file);
});

window.downloadPNG = function() {
    const dataURL = canvas.toDataURL({ format: 'png', quality: 1 });
    const link = document.createElement('a');
    link.download = 'classified-export.png';
    link.href = dataURL;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
};

function renderLayers() {
    layersList.innerHTML = '';
    const objects = canvas.getObjects();
    
    objects.forEach((obj, i) => {
        const li = document.createElement('li');
        li.className = `layer-item border border-[#00ffcc] bg-black p-2 text-xs flex justify-between items-center ${canvas.getActiveObject() === obj ? 'shadow-[inset_0_0_10px_rgba(0,255,204,0.5)]' : ''}`;
        
        li.innerHTML = `
            <div class="flex flex-col truncate w-1/2">
                <span class="font-bold text-[#00ffcc]">#${i} ${obj.name || obj.type}</span>
            </div>
            <div class="flex gap-1">
                <button title="Subir" class="cyber-btn px-2" onclick="changeZ(${i}, 1)">↑</button>
                <button title="Bajar" class="cyber-btn px-2" onclick="changeZ(${i}, -1)">↓</button>
                <button title="Eliminar" class="text-red-500 border border-red-500 px-2 hover:bg-red-500 hover:text-black" onclick="removeLayer(${i})">X</button>
            </div>
        `;
        li.onclick = (e) => {
            if(e.target.tagName !== 'BUTTON') { canvas.setActiveObject(obj); canvas.renderAll(); }
        };
        layersList.prepend(li);
    });
}

window.changeZ = function(index, delta) {
    const obj = canvas.item(index);
    if(!obj) return;
    if(delta > 0) canvas.bringForward(obj); else if(index > 0) canvas.sendBackwards(obj);
    canvas.renderAll(); renderLayers();
};
window.removeLayer = function(index) {
    const obj = canvas.item(index);
    if(obj) { canvas.remove(obj); canvas.renderAll(); renderLayers(); }
};

