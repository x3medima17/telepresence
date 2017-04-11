THREE.Mesh.prototype.get_vector = function(){
	return new Vector3(this.position.x, this.position.y, this.position.z)
}

function Arm(data, SCALE) {
	this.Joints = {}
	for(var joint in data) {
		curr = data[joint]
		console.log(curr)
		this.Joints[joint] = new THREE.Vector3(curr[0], curr[1], curr[2])
		this.Joints[joint].multiplyScalar(SCALE)
	}
}

Arm.prototype.update = function(data) {
	for(var joint in this.Joints) {
		curr = data[joint]
		this.Joints[joint].position.set(curr[0], curr[1], curr[2])
		this.Joints[joint].multiply(SCALE)
	}
}

Arm.prototype.publish = function(scene) {
	for(var joint in this.Joints) 
		scene.add(this.Joints[joint])
}

Arm.prototype.get_joints = function() {
	lst = []
	for(var joint in this.Joints)
		lst.push(this.Joints[joint])
	return lst
}

function DataSet(data) {
	this.left = new Arm(data["left"], 100)
	this.right = new Arm(data["right"], 100)
}

DataSet.prototype.update = function(data){
	this.left.update(data["left"])
	this.right.update(data["right"])
}

DataSet.prototype.publish = function(scene){
	this.left.publish(scene)
	this.right.publish(scene)

}
DataSet.prototype.get_objects = function(){
	out = this.left.get_joints()
	return out.concat(this.right.get_objects())
}


function vec_from_mesh(mesh) {
	var vec = new THREE.Vector3()
	vec.x = mesh.position.x
	vec.y = mesh.position.y
	vec.z = mesh.position.z
	return vec
}

function vec_from_arr(arr){
	var vec = new THREE.Vector3(arr[0], arr[1], arr[2])
	return vec
	
}
function remove_axis(vec, index) {
	//0-x, 1-y, 2-z
	var tmp = new THREE.Vector3()
	tmp.x = vec.x
	tmp.y = vec.y
	tmp.z = vec.z
	if(index == 0)
		tmp.x = 0
	else if (index == 1)
		tmp.y = 0
	else
		tmp.z = 0
	return tmp 
}

function switch_coords_arr(arr) {
	return [-arr[2], -arr[0], arr[1]]
}


function swict_coords_arr_back(arr) {
	return [-arr[1], arr[2], -arr[0] ]
}

function clone(obj) {
    if (null == obj || "object" != typeof obj) return obj;
    var copy = obj.constructor();
    for (var attr in obj) {
        if (obj.hasOwnProperty(attr)) copy[attr] = clone(obj[attr]);
    }
    return copy;
}

function translate_arm(hand, translation) {
	//translation: [x,y,z]
	out = clone(hand)
	for(var joint in out)
		for(var i = 0; i<3; i++)
			out[joint][i] += translation[i]
	return out
}