function setup(width,height)
{
			// Setup camera
		scene = new THREE.Scene()
		var SCREEN_WIDTH = width,
			SCREEN_HEIGHT = height,
			VIEW_ANGLE = 40,
			ASPECT = SCREEN_WIDTH / SCREEN_HEIGHT ,
			NEAR = 1.1,
			FAR = 20000

		camera = new THREE.PerspectiveCamera(VIEW_ANGLE, ASPECT, NEAR, FAR)

		scene.add(camera)
		camera.position.set(0,100,-200)
		camera.lookAt(scene.position)

		// Render
		if(Detector.webgl)
			renderer = new THREE.WebGLRenderer({ antilialias:true })
			else
			renderer = new THREE.CanvasRenderer()

		renderer.setSize(SCREEN_WIDTH, SCREEN_HEIGHT)

		container = document.getElementById("ThreeJS")
		container.appendChild(renderer.domElement)

		// Auto-resize
		THREEx.WindowResize(renderer,camera)
		THREEx.FullScreen.bindKey({charCode:'m'.charCodeAt(0)})

		// Controls
		controls = new THREE.OrbitControls(camera, renderer.domElement)

		// Stats
		stats = new Stats()
		stats.domElement.style.position = 'absolute'
		stats.domElement.style.bottom = '0px'
		stats.domElement.style.zIndex = 100
		// container.appendChild(stats.domElement)

		// Light
		light = new THREE.DirectionalLight(0xffffff);

	    light.position.set(200, 400, -400);
	    light.castShadow = true;
	    light.shadowCameraLeft = -60;
	    light.shadowCameraTop = -60;
	    light.shadowCameraRight = 60;
	    light.shadowCameraBottom = 60;
	    light.shadowCameraNear = 1;
	    light.shadowCameraFar = 1000;
	    light.shadowBias = -.0001
	    light.shadowMapWidth = light.shadowMapHeight = 1024;
	    light.shadowDarkness = .7;
	    scene.add(light);

		//scene.add(ambientLight) // Pod voprosom


		/// Axes !
		var axes = new THREE.AxisHelper(100)
		scene.add(axes)


		// Floor
		var floorTexture = new THREE.ImageUtils.loadTexture('static/img/checkerboard.jpg')
		floorTexture.wrapS = floorTexture.wrapT = THREE.RepeatWrapping;
		floorTexture.repeat.set(10,10)

		var floorMaterial = new THREE.MeshBasicMaterial({ map: floorTexture, side: THREE.DoubleSide })
		var floorGeometry = new THREE.PlaneGeometry(250,250,1,1)
		var floor = new THREE.Mesh(floorGeometry, floorMaterial)
		floor.position.y = -0.5
		floor.rotation.x = Math.PI /2
		scene.add(floor)


		
}

