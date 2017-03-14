var GRS = {
	wrist : {
		position : {
			x : -70,
			y : 120,
			z : 50
		},
		pitch : 0,
		roll : 0,
		heading : 0,
		object : undefined
	},

	thumb : {
		wrist_angle : 2.87979327,
		finger_angle : 2.26543737,

		distal : 1.42,
		proximal : 2.39,
		metacarpal : 3.68,
		wrist : 1.75,

		roll : 0,
		pitch : 0,
		heading : 0,

		joints : [],
		bones : []
	},

	index : {
		wrist_angle : 2.26892803 ,
		finger_angle : 1.65457213 ,

		distal : 1.25,
		intermediate : 1.63, 
		proximal : 2.93,
		metacarpal : 5.04,
		wrist : 1.76,
		
		heading : 0,
		pitch : 0.9,
		roll : 0, 

		joints : [],
		bones : []	
	},

	middle : {
		wrist_angle : 1.57079633,
		finger_angle : 1.44862328,
		
		distal : 1.36,
		intermediate : 1.9, 
		proximal : 3.26,
		metacarpal : 4.80,
		wrist : 1.40,
		
		heading : 0,
		pitch : 1.3,
		roll : 0, 

		joints : [],
		bones : []	
	},	

	ring : {
		wrist_angle : 1.19205988,
		finger_angle : 1.29154365,
	
		distal : 1.31,
		intermediate : 1.79, 
		proximal : 3,
		metacarpal : 4.4,
		wrist : 1.41,  
	
		heading : 0,
		pitch : 1,
		roll : 0,

		joints : [],
		bones : []	 
	},

	pinky : {
		wrist_angle : 0.591666616,
		finger_angle : 1.14319066,
	
		distal : 1.17,
		intermediate : 1.35, 
		proximal : 2.39,
		metacarpal : 4.2,
		wrist : 1.71,
	
		heading : 0,
		pitch : 1.1,
		roll : 0,  

		joints : [],
		bones : []	
	},
	scale : 15,
	objects : []
}

var bone_template = {
	position : {
		x : 0,
		y : 0,
		z : 0
	},

	rotation : {
		heading : 0,
		roll : 0,
		pitch : 0
	},

	object : undefined

}


var joint_template = {
	position : {
		x : 0,
		y : 0,
		z : 0
	},
	spin : {
		heading : 0,
		roll : 0,
		pitch : 0
	},
	length : 0,
	object : undefined

}

/*
window.GRS = function(){

	this.objects = function(){
		this.thumb  = "hello"
		this.index  = []
		this.middle = []
		this.ring   = []
		this.pinky  = []
		this.misc   = []
		this.add = function(object,finger)
		{
			this[finger].push(object)
		}
	}

	this.Object = function(geometry,material,x,y,z){
		var obj = new THREE.Mesh(geometry,material)
		obj.position.set(x,y,z)
		return obj

	}
}
*/
