
var wristSphereGeometry = new THREE.SphereGeometry(10,36,16)
var tipSphereGeometry = new THREE.SphereGeometry(4	,36,16)
var sphereMaterial = new THREE.MeshLambertMaterial({ color:0xff0000, opacity:0.9 })

var cylinderMaterial = new THREE.MeshNormalMaterial({color : 0xcccccc})

var cylinderGeometry  = new THREE.CylinderGeometry(5,1,200,10)	

cylinderGeometry.applyMatrix( new THREE.Matrix4().makeRotationX( - Math.PI / 2 ) ); 


boneGeometry = function(len) {
	tmp = new THREE.CylinderGeometry(2,2,len,32,32,false)
	tmp.applyMatrix( new THREE.Matrix4().makeTranslation( 0, len / 2, 0 ) );
	tmp.applyMatrix( new THREE.Matrix4().makeRotationX(	 THREE.Math.degToRad( 90 ) ) );
	return tmp
}