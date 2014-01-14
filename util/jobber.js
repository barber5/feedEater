var validate = require('./validate').validate
var fs = require('fs')
var knox = require('knox')
var mime = require('mime')
//var myS3Account = new s3('AKIAJUBWKTOX2SHDHCXA', 'MFCaKIa0CTOFEjDQ/u7wrx9jRJCyQmS07PF5NLYI');
var client = knox.createClient({
    key: 'AKIAJUBWKTOX2SHDHCXA'
  , secret: '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'
  , bucket: 'etheaimages'
});

var winston = require('winston');
var mylogger = new(winston.Logger)({
	transports: [
		new (winston.transports.Console)({timestamp: true})
	]
});

module.exports.jobber = function(requirements, response, gearman, jobname) {
	var valid = validate(requirements)

	if(typeof(valid.error) === 'undefined') {
		console.log(JSON.stringify(valid))
		var job = gearman.submitJob(jobname, JSON.stringify(valid))
		job.on("data", function(data){			
			console.log(data)	
			jsonData = JSON.parse(data)
			if(typeof(jsonData.error) === 'undefined') {
				response.json({
					"status": "ok",
					"result": jsonData
				});
				return
			}
			else {
				response.json({
					"status": "error",
					"result": {},
					"error" : jsonData.error
				});
				return	
			}
		});

		job.on("timeout", function(){
			response.json({
				"status":"error", 
				"result": {},
				"error":"timeout"
			});
			return
		});

		job.on("error", function(error){
			console.log('node error got')
			console.log(error)
			console.log(error.message)
			response.json({
				"status":"error", 
				"result": {},
				"error": error.message
			});
			return
		});
	} 
	else {
		response.json({
			'status': 'error',			
			'result' : {},
			'error' : valid.error
		})
	}
}

module.exports.uploader = function(requirements, response) {
	var valid = validate(requirements)

	if(typeof(valid.error) === 'undefined') {		
		var path = valid.path		
		require('crypto').randomBytes(4, function(ex, buf) {
			var dt = new Date()
			var name = dt.getFullYear()+'-'+(dt.getMonth()+1)+'-'+dt.getDate()+'/'+valid.ethean_id+buf.toString('hex');
		
			var size = valid.size
		    var stream = fs.createReadStream(path)
		    var mimetype = mime.lookup(path);
		    var req;

		    if (mimetype.localeCompare('image/jpeg') || mimetype.localeCompare('image/pjpeg') || mimetype.localeCompare('image/png') || mimetype.localeCompare('image/gif')) {
		        winston.info('got correct type: '+JSON.stringify(valid))
		        req = client.putStream(stream, name,
		            {
		                'Content-Type': mimetype,
		                'Cache-Control': 'max-age=604800',
		                'x-amz-acl': 'public-read',
		                'Content-Length': size
		            },
		            function(err, res) {
		                if(err) {
		                	response.json({
								'status': 'error',			
								'result' : {},
								'error' : JSON.stringify(err)
							})
		                }
		                else {
		                	winston.info('putstream callback')
		                	res.resume();	                	
		                }
		            }
		       	)
		       	winston.info('putstreamd')
		        req.on('response', function(res){
					if (res.statusCode == 200) {
						response.json({
							'status': 'ok',
							'result': {
								'url': req.url	
							}						
						})
					} else {
						response.json({
							'status': 'error',			
							'result' : {},
							'error' : "http error statuscode" + JSON.stringify(res.statusCode)
						})
					}
				})
				req.on('progress', function(prog) {
					winston.info("progress")
					winston.info(prog)
				}) 
			} else {
				response.json({
					'status': 'error',			
					'result' : {},
					'error' : "unsupported format for upload"
				})
			}
			fs.unlink(path, function(err) {
				if(err) {
					winston.error("problem deleting uploaded file: "+JSON.stringify(valid)+" error: "+JSON.stringify(err))
				}
			})	
		});
	}
	else {
		response.json({
			'status': 'error',			
			'result' : {},
			'error' : valid.error
		})
	}
}

module.exports.downloader = function(requirements, response) {	
	var url = myS3Account.readPolicy('myfile', 'mybucket', 60);
}

	
