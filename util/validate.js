var check = require('validator').check,
    sanitize = require('validator').sanitize


var winston = require('winston');
var mylogger = new(winston.Logger)({
	transports: [
		new (winston.transports.Console)({timestamp: true})
	]
});
var validationError = {"error" : "validation error"}

module.exports.b_QO = function(req) {
	return {
		"body": req.body
	}
}

module.exports.q_QO = function(req) {
	return {
		"query": req.query
	}
}

module.exports.bq_QO = function(req) {
	return {
		"body": req.body,
		"query": req.query
	}
}

module.exports.bp_QO = function(req) {
	return {
		"body": req.body,
		"params": req.params
	}
}

module.exports.pq_QO = function(req) {
	return {
		"params": req.params,
		"query": req.query
	}
}

module.exports.name_REQ = function(qo, opt) {
	var result = {
		queryObject: qo,
		selector: ['name'],
		fieldName: 'name',
		constraints: [{
			'name': 'lengthMin',
			'value': 1
		},{
			'name': 'lengthMax',
			'value': 255
		}]
	}
	if(opt) {
		result.isOptional = true
	}
	return result
}

module.exports.title_REQ = function(qo, opt) {
	var result = {
		queryObject: qo,
		selector: ['title'],
		fieldName: 'title',
		constraints: [{
			'name': 'lengthMin',
			'value': 1
		},{
			'name': 'lengthMax',
			'value': 255
		}]
	}
	if(opt) {
		result.isOptional = true
	}
	return result
}


module.exports.description_REQ = function(qo, opt) {
	var result = {
		queryObject: qo,
		selector: ['description'],
		fieldName: 'description',
		constraints: [{
			'name': 'lengthMax',
			'value': 2048
		}]
	}
	if(opt) {
		result.isOptional = true
	}
	return result
}

module.exports.image_REQ = function(qo, opt) {
	var result = {
		queryObject: qo,
		selector: ['image'],
		fieldName: 'image',
		constraints: [{
			'name': 'lengthMax',
			'value': 255
		}]
	}
	if(opt) {
		result.isOptional = true
	}
	return result
}

module.exports.access_token_REQ = function(qo, opt) {
	var result = {
		queryObject: qo,
		selector: ['access_token'],
		fieldName: 'access_token',
		constraints: [{
			'name': 'lengthMax',
			'value': 512
		}]
	}
	if(opt) {
		result.isOptional = true
	}
	return result
}

module.exports.email_REQ = function(qo, opt) {
	var result = {
		queryObject: qo,
		selector: ['email'],
		fieldName: 'email',
		constraints: [{
			'name': "email",
			'value': ""
		}, {
			'name': 'lengthMin',
			'value': 1
		},{
			'name': 'lengthMax',
			'value': 255
		}]
	}
	if(opt) {
		result.isOptional = true
	}
	return result
}

module.exports.password_REQ = function(qo, opt) {
	var result = {
		queryObject: qo,
		selector: ['password'],
		fieldName: 'password',
		constraints: [{
			'name': 'lengthMin',
			'value': 1
		},{
			'name': 'lengthMax',
			'value': 255
		}]
	}
	if(opt) {
		result.isOptional = true
	}
	return result
}

module.exports.uuid_REQ = function(idname, qo, opt) {
	var result = {
		queryObject: qo,
		selector: [idname],
		fieldName: idname,
		constraints: [{
			'name': 'uuid',
			'value': ''
		}]
	}
	if(opt) {
		result.isOptional = true
	}
	return result
}

var uuid_list_REQ = function(idname, qo, opt) {
	var result = {
		queryObject: qo,
		selector: [idname],
		fieldName: idname,
		isList: true,
		constraints: [{
			'name': 'uuid',
			'value': ''
		}]
	}
	if(opt) {
		result.isOptional = true
	}
	return result	
}

module.exports.uuid_list_REQ = uuid_list_REQ

module.exports.flag_REQ = function(qo, opt) {
	var result = {
		queryObject: qo,
		selector: ['flag'],
		fieldName: 'flag',
		constraints: [{
			'name': 'lengthMax',
			'value': 255
		}]
	}
	if(opt) {
		result.isOptional = true
	}
	return result
}

module.exports.points_REQ = function(qo, opt) {
	var result = {
		queryObject: qo,
		selector: ['points'],
		fieldName: 'points',
		constraints: [{
			'name': 'int',
			'value': ''
		}]
	}
	if(opt) {
		result.isOptional = true
	}
	return result
}

var content_REQ = function(qo, opt) {
	var result = {
		queryObject: qo,
		selector: ['content'],
		fieldName: 'content',
		constraints: [{
			'name': 'lengthMin',
			'value': 0
		},{
			'name': 'lengthMax',
			'value': 2048
		}]
	}
	if(opt) {
		result.isOptional = true
	}
	return result
}

module.exports.content_REQ = content_REQ

var structure_type_REQ = function(qo, opt) {
	var result = {
		queryObject: qo,
		selector: ['structure_type'],
		fieldName: 'structure_type',
		constraints: [{
			'name': 'lengthMin',
			'value': 0
		},{
			'name': 'lengthMax',
			'value': 255
		}]
	}
	if(opt) {
		result.isOptional = true
	}
	return result
}
module.exports.structure_type_REQ = structure_type_REQ

module.exports.limit_REQ = {
	queryObject: "query",
	selector: ['limit'],
	fieldName: 'limit',
	isOptional: true,
	constraints: [{
		'name': 'int',
		'value': ''
	}]
}

module.exports.offset_REQ =  {
	queryObject: "query",
	selector: ['offset'],
	fieldName: 'offset',
	isOptional: true,
	constraints: [{
		'name': 'int',
		'value': ''
	}]
}

function checkStructure(value) {
	var requirements = {
		queryObjects: {
			"body": value
		},
		requirements: [
			content_REQ('body'),
			structure_type_REQ('body'),
			uuid_list_REQ('items', 'body')
		]
	}
	return validate(requirements)		
}

// tries to select arguments[1:] from obj
function magic_sel(obj) {
	try {
		var nextObj = obj;		
		for(var i = 1; i < arguments.length; i++) {		
			nextObj = nextObj[arguments[i]]
		}
		return nextObj
	}
	catch(e) {
		return undefined
	}
}


// tries to select sel (an array) from obj
function magic_sel_array(obj, sel) {
	try {
		var nextObj = obj;		
		for(var i = 0; i < sel.length; i++) {		
			nextObj = nextObj[sel[i]]
		}
		return nextObj
	}
	catch(e) {
		return undefined
	}	
}

// if val is undefined or null return true
function no_value(val) {
	if(typeof(val) === 'undefined' || val == null) {
		return true
	}
	else {
		return false
	}
}

function no_value_sel(obj) {
	if(no_value(obj)) {
		return true
	}
	for(var i = 1; i < arguments.length; i++) {
		var nextVal = magic_sel_array(obj, arguments[i])
		if(no_value(nextVal))
			return true
	}
	return false
}


// returns true if constraint fails
function check_constraint(constraint, value) {
	try {
		switch(constraint.name) {
			case "uuid": 
				check(value).isUUIDv4()
			break;
			case "not empty":
				check(value).notEmpty()
			break;
			case "int":
				check(value).isInt()
			break;
			case "alphanumeric":
				check(value).isAlphanumeric()
			break;
			case "url":
				check(value).isUrl()
			break;
			case "email":
				check(value).isEmail()
			break;
			case "lengthMin":
				check(value).len(constraint.value)
			break;
			case "lengthMax":
				check(value).len(0, constraint.value)
			break;
			case "structure":
				var result = checkStructure(value)
				winston.info('validated structure and got '+JSON.stringify(result))				
				if(typeof(result.error) !== 'undefined') {
					return true
				}				
			break;
			default:
				return validationError
			break;
		}
	}
	catch(e) {
		return true
	}
}

function sanitize_value(how, value) {
	try {
		switch(how) {
			case "int": 
				return sanitize(value).toInt()
			break;
			default:
				return undefined
			break;
		}
	}
	catch(e) {
		return undefined
	}
}

/* 	This will abstract validation for node requests

	requirementsDict needs to have a field called queryObjects which will be an object
	mapping names to objects

	requirementsDict needs to have a field called requirements which is an array of requirement
	objects

	requirement objects in the requirementsDict.requirements array need to have a field called 
	queryObject which is the index of the query object defined in requirementsDict.queryObjects 
	that we will be using to check this requirement

	requirement objects need to have a field called selector which tells how to get the value
	we will be checking out of the queryObject

	requirement objects need to have an field called constraints which is an array of constraint objects

	requirement objects have an optional field called isList which just flags whether the test value is
	a list of objects to which the constraints should be applied

	requirement objects also hve an optional field called isOptional which indicates that the value at
	the requirement.selector of requirement.queryObject is allowed to be unknown/null and if it is we
	can skip all constraint checking

	requirement objects have an optional field called sanitize which says how testValue should be sanitized
	via a subfield called how

	requirement processing is short-circuiting, so if it fails any requirement an error
	is returned immediately
	
*/
var validate = function(requirementDict) {	
	winston.info(requirementDict)
	//console.log(JSON.stringify(requirementDict))
	// make sure requirementDict has the two required fields
	if(no_value_sel(requirementDict, ['queryObjects'], ['requirements'])) {
		winston.error('malformed requirementDict')
		return validationError
	}	
	var result = {}
	var queryObjs = requirementDict.queryObjects;	
	// iterate through our requirements	
	for(prop in requirementDict.requirements) {
		var requirement = requirementDict.requirements[prop]
		winston.info('new requirement: '+JSON.stringify(requirement))
		// requirement needs to have a queryObject, selector, fieldName, and constraints
		if(no_value_sel(requirement, ['queryObject'], ['selector'], ['fieldName'], ['constraints'])) {
			winston.error('malformed requirement')
			return validationError
		}		
		var queryObject = queryObjs[requirement.queryObject]
		if(no_value(queryObject)) {
			winston.error('malformed queryObject')
			console.log(queryObject)
			return validationError
		}
		var selector = requirement.selector
		var testValue = magic_sel_array(queryObject, selector)
		var fieldName = requirement.fieldName
		var constraints = requirement.constraints

		// if testValue is allowed to be null/undefined, and it actually is then we want to do no further checking
		var resValue = undefined
		if(requirement.isOptional && no_value(testValue)) {
			winston.info(fieldName + " is allowed to be null, moving on...")
			
		} 
		// if testValue is null/undefined and not allowed to be, terminate immediately
		else if(no_value(testValue)) {
			winston.error(fieldName + " was null when it shouldn't have been")
			return {"error": fieldName}
		}
		// testValue not null/undefined, proceed
		else {
			winston.info("processing "+fieldName)
			// process the constraints for this fieldName
			for(c in constraints) {
				var constraint = constraints[c]
				winston.info("constraint: "+JSON.stringify(constraint))
				winston.info('test value is '+JSON.stringify(testValue))
				// have we been given correct format for constraints?
				if(no_value_sel(constraint, ['name'], ['value'])) {		
					winston.error('malformed constraint')	
					return validationError
				}				
				// isList flag set?  if so, process slightly differently
				if(requirement.isList) {
					if(typeof(testValue) !== typeof([])) {
						winston.error('isList was set but value not a list')
						return validationError
					}
					for(var i = 0; i < testValue.length; i++) {						
						var nextFail = check_constraint(constraint, testValue[i])
						if(nextFail) {
							winston.error(JSON.stringify(nextFail))
							return {"error": fieldName}
						}
					}
				}
				else {
					var nextFail = check_constraint(constraint, testValue)
					
					if(nextFail) {
						winston.error(JSON.stringify(nextFail))
						return {"error": fieldName}
					}	
				}
			} // process next constraint
			// passed all constraint checks, now let's see if we have to sanitize anything
			winston.info('passed constraint checks')
			if(!no_value(requirement.sanitize)) {	
				var sanit = requirement.sanitize
				if(no_value_sel(sanit, ['how'])) {
					return validationError
				}		
				var how = sanit.how
				// treat lists in a special way
				if(requirement.isList) {
					var saniList = []
					// sanitize everything in the list
					for(var i = 0; i < testValue.length; i++) {
						var nextValue = sanitize_value(how, testValue[i])
						if(no_value_sel(nextValue)) {
							return validationError
						}
						saniList.push(nextValue)
					}
					resValue = saniList
				}
				// non-list
				else {
					// just sanitize this guy
					var nextValue = sanitize_value(how, testValue)
					if(no_value_sel(nextValue)) {
						return validationError
					}
					resValue = nextValue

				}
			}
			else {
				// no sanitization required, copy value straight out
				resValue = testValue
			}
		} // done processing fieldName, if we get here all constraints passed and sanitization happened successfully
		winston.info('done processing ')	
		// add this guy to the result, defult is undefined which won't show up on the other side of gearman as None, just won't exist
		result[fieldName] = resValue
	} // process next requirement
	return result
}
module.exports.validate = validate