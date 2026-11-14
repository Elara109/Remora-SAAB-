
import base64
from pathlib import Path

import streamlit.components.v1 as components


ROOT = Path(__file__).resolve().parent.parent


def show_deployment(height=550):
    main_path = ROOT / "models" / "main_auv.glb"
    mini_path = ROOT / "models" / "mini_rov.glb"

    main_data = base64.b64encode(
        main_path.read_bytes()
    ).decode("ascii")

    mini_data = base64.b64encode(
        mini_path.read_bytes()
    ).decode("ascii")

    html = """
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">

<style>
    body {
        margin: 0;
        overflow: hidden;
        background: #071b30;
        font-family: Arial, sans-serif;
        color: white;
    }

    #scene {
        width: 100vw;
        height: 100vh;
    }

    #status {
        position: absolute;
        top: 15px;
        left: 15px;
        padding: 12px 16px;
        background: rgba(0, 0, 0, 0.7);
        border-radius: 8px;
        z-index: 10;
    }

    .buttons {
        position: absolute;
        bottom: 20px;
        left: 20px;
        display: flex;
        gap: 10px;
        z-index: 10;
    }

    button {
        padding: 12px 20px;
        color: white;
        border: none;
        border-radius: 8px;
        cursor: pointer;
        font-weight: bold;
    }

    button:disabled {
        opacity: 0.45;
        cursor: not-allowed;
    }

    #deploy {
        background: #16a34a;
    }

    #return {
        background: #2563eb;
    }
</style>

<script type="importmap">
{
    "imports": {
        "three": "https://cdn.jsdelivr.net/npm/three@0.160.1/build/three.module.js",
        "three/addons/": "https://cdn.jsdelivr.net/npm/three@0.160.1/examples/jsm/"
    }
}
</script>
</head>

<body>

<div id="status">Mini ROV Status: LOADING</div>

<div class="buttons">
    <button id="deploy" disabled>Deploy Mini ROV</button>
    <button id="return" disabled>Return to Dock</button>
</div>

<div id="scene"></div>

<script type="module">
import * as THREE from "three";
import { GLTFLoader } from "three/addons/loaders/GLTFLoader.js";
import { OrbitControls } from "three/addons/controls/OrbitControls.js";

const container = document.getElementById("scene");
const status = document.getElementById("status");
const deployButton = document.getElementById("deploy");
const returnButton = document.getElementById("return");

const scene = new THREE.Scene();
scene.background = new THREE.Color(0x071b30);

const camera = new THREE.PerspectiveCamera(
    45,
    window.innerWidth / window.innerHeight,
    0.1,
    1000
);

const renderer = new THREE.WebGLRenderer({
    antialias: true
});

renderer.setSize(
    window.innerWidth,
    window.innerHeight
);

renderer.setPixelRatio(
    Math.min(window.devicePixelRatio, 2)
);

container.appendChild(renderer.domElement);

scene.add(new THREE.HemisphereLight(
    0xffffff,
    0x355577,
    2
));

const light = new THREE.DirectionalLight(
    0xffffff,
    3
);

light.position.set(5, 10, 7);
scene.add(light);

const controls = new OrbitControls(
    camera,
    renderer.domElement
);

controls.enableDamping = true;

const loader = new GLTFLoader();

let mainAUV = null;
let miniROV = null;

const dockPosition = new THREE.Vector3();
const inspectionPosition = new THREE.Vector3();

const startPosition = new THREE.Vector3();
const endPosition = new THREE.Vector3();

let moving = false;
let returning = false;
let animationStart = 0;


function centerModel(model) {
    const box = new THREE.Box3().setFromObject(model);
    const center = box.getCenter(new THREE.Vector3());

    model.position.sub(center);
    model.updateMatrixWorld(true);
}

function findDockingZone(model) {
    let found = null;
    let bestOrange = null;
    let bestScore = -1;

    model.traverse((object) => {
        if (!object.isMesh) return;

        const name = object.name.toLowerCase();

        if (
            name.includes("mini_rov_docking_zone") ||
            (name.includes("dock") && name.includes("zone"))
        ) {
            found = object;
        }

        // Backup: identify the orange mesh by its material.
        const materials = Array.isArray(object.material)
            ? object.material
            : [object.material];

        for (const mat of materials) {
            if (!mat || !mat.color) continue;

            const c = mat.color;
            const score = c.r - (c.g + c.b) / 2;

            if (
                c.r > 0.45 &&
                c.r > c.g * 1.15 &&
                c.g > c.b * 1.25 &&
                score > bestScore
            ) {
                bestOrange = object;
                bestScore = score;
            }
        }
    });

    const object = found || bestOrange;

    if (!object) return null;

    object.updateWorldMatrix(true, false);

    const box = new THREE.Box3().setFromObject(object);

    return {
        object,
        center: box.getCenter(new THREE.Vector3()),
        size: box.getSize(new THREE.Vector3()),
        foundByName: !!found
    };
}


function setupModels() {
    if (!mainAUV || !miniROV) return;

    mainAUV.updateMatrixWorld(true);

    const mainBox = new THREE.Box3().setFromObject(mainAUV);
    const mainCenter = mainBox.getCenter(new THREE.Vector3());
    const mainSize = mainBox.getSize(new THREE.Vector3());
    const mainLength = Math.max(mainSize.x, mainSize.y, mainSize.z);

    const dock = findDockingZone(mainAUV);

    if (!dock) {
        status.innerText = "ERROR: Docking zone not found";
        return;
    }

    // The uploaded GLB confirms that the dock faces +Z.
    const outward = new THREE.Vector3(0, 0, 1);

    // Make the Mini ROV visible.
    miniROV.visible = true;

    // Scale the Mini ROV.
    const miniOriginalBox = new THREE.Box3().setFromObject(miniROV);
    const miniOriginalSize = miniOriginalBox.getSize(new THREE.Vector3());
    const miniLength = Math.max(
        miniOriginalSize.x,
        miniOriginalSize.y,
        miniOriginalSize.z
    );

    if (miniLength > 0) {
        miniROV.scale.multiplyScalar(
            mainLength * 0.18 / miniLength
        );
    }

    miniROV.updateMatrixWorld(true);

    // Read the Mini ROV's actual bounding box.
    const miniBox = new THREE.Box3().setFromObject(miniROV);
    const miniCenter = miniBox.getCenter(new THREE.Vector3());
    const miniSize = miniBox.getSize(new THREE.Vector3());

    // Attach it to the OUTER surface of the orange dock.
    const targetCenter = new THREE.Vector3(
        dock.center.x,
        dock.center.y,
        dock.center.z + dock.size.z / 2 + miniSize.z / 2
    );

    // Move the actual geometry, not just its assumed origin.
    const correction = targetCenter.clone().sub(miniCenter);
    miniROV.position.add(correction);
    miniROV.updateMatrixWorld(true);

    // Save the exact docking position.
    dockPosition.copy(miniROV.position);

    // Deployment goes away from the dock.
    inspectionPosition.copy(dockPosition);
    inspectionPosition.z += mainLength * 0.65;
    inspectionPosition.y -= mainLength * 0.12;

    // Camera.
    camera.position.set(
        mainCenter.x + mainLength * 1.2,
        mainCenter.y + mainLength * 0.9,
        mainCenter.z + mainLength * 1.4
    );

    controls.target.copy(mainCenter);
    controls.update();

    status.innerText = "Mini ROV Status: DOCKED | GLB FIX";
    deployButton.disabled = false;
    returnButton.disabled = true;
}


const mainURL =
    "data:model/gltf-binary;base64,MAIN_DATA";

const miniURL =
    "data:model/gltf-binary;base64,MINI_DATA";

loader.load(
    mainURL,
    function(gltf) {
        mainAUV = gltf.scene;

        centerModel(mainAUV);
        scene.add(mainAUV);

        setupModels();
    },
    undefined,
    function(error) {
        status.innerText = "Main AUV loading failed";
        console.error(error);
    }
);

loader.load(
    miniURL,
    function(gltf) {
        miniROV = gltf.scene;

        centerModel(miniROV);
        miniROV.visible = true;
        scene.add(miniROV);

        setupModels();
    },
    undefined,
    function(error) {
        status.innerText = "Mini ROV loading failed";
        console.error(error);
    }
);

function beginMovement(destination, isReturning) {
    if (!miniROV || moving) return;

    startPosition.copy(miniROV.position);
    endPosition.copy(destination);

    returning = isReturning;
    moving = true;

    animationStart = performance.now();

    deployButton.disabled = true;
    returnButton.disabled = true;

    status.innerText = returning
        ? "Mini ROV Status: RETURNING"
        : "Mini ROV Status: DEPLOYING";
}

deployButton.addEventListener("click", () => {
    beginMovement(inspectionPosition, false);
});

returnButton.addEventListener("click", () => {
    beginMovement(dockPosition, true);
});

function animate(time) {
    requestAnimationFrame(animate);

    if (moving && miniROV) {
        const progress = Math.min(
            (time - animationStart) / 5000,
            1
        );

        const smooth =
            progress * progress * (3 - 2 * progress);

        miniROV.position.lerpVectors(
            startPosition,
            endPosition,
            smooth
        );

        if (progress >= 1) {
            moving = false;

            if (returning) {
                miniROV.position.copy(dockPosition);

                status.innerText =
                    "Mini ROV Status: DOCKED";

                deployButton.disabled = false;
                returnButton.disabled = true;
            } else {
                miniROV.position.copy(
                    inspectionPosition
                );

                status.innerText =
                    "Mini ROV Status: INSPECTION POSITION";

                deployButton.disabled = true;
                returnButton.disabled = false;
            }
        }
    }

    controls.update();
    renderer.render(scene, camera);
}

animate(0);

window.addEventListener("resize", () => {
    camera.aspect =
        window.innerWidth / window.innerHeight;

    camera.updateProjectionMatrix();

    renderer.setSize(
        window.innerWidth,
        window.innerHeight
    );
});
</script>
</body>
</html>
"""

    html = html.replace("MAIN_DATA", main_data)
    html = html.replace("MINI_DATA", mini_data)

    components.html(
        html,
        height=height,
        scrolling=False
    )
