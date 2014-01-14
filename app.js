// dbuser: feedman dbpass: feedpass
// http://sequelizejs.com/documentation
var Sequelize = require("sequelize")

var cluster = require('cluster')
var numCPUs = require('os').cpus().length;
var winston = require('winston');
var mylogger = new(winston.Logger)({
	transports: [
		new (winston.transports.Console)({timestamp: true})
	]
});

if ( cluster.isMaster ) {
	mylogger.info('master started: starting %d workers ', numCPUs);
	cluster.on('exit', function(deadWorker, code, signal) {
		// Restart the worker
		var worker = cluster.fork();

		// Note the process IDs
		var newPID = worker.process.pid;
		var oldPID = deadWorker.process.pid;

		// Log the event
		mylogger.error('worker '+oldPID+' died.');
		mylogger.error('worker '+newPID+' born.');
	});

	for ( var i=0; i<numCPUs; ++i ) {
		cluster.fork();
	}
}

else {
	var express = require('express')	  	  
	, http = require('http')
	, path = require('path')
	, async = require('async')	  
	, app = express();

	var sequelize = new Sequelize('feed', 'feedman', 'feedpass', {
		dialect: 'postgres'
	})


	// all environments
	app.set('port', process.env.PORT || 3000);
	app.set('views', __dirname + '/views');
	//app.engine('html', require('ejs').renderFile);
	app.use(express.favicon());
	app.use(express.static(path.join(__dirname, 'public')));
	app.use(express.logger('dev'));
	app.use(express.cookieParser());
	app.use(express.bodyParser());
	app.use(express.methodOverride());


	app.use(app.router);
	// Since this is the last non-error-handling
	// middleware use()d, we assume 404, as nothing else
	// responded.

	app.use(function(req, res, next){
		// the status option, or res.statusCode = 404
		// are equivalent, however with the option we
		// get the "status" local available as well
		res.render('404', { status: 404, url: req.url });
	});

	// error-handling middleware, take the same form
	// as regular middleware, however they require an
	// arity of 4, aka the signature (err, req, res, next).
	// when connect has an error, it will invoke ONLY error-handling
	// middleware.

	// If we were to next() here any remaining non-error-handling
	// middleware would then be executed, or if we next(err) to
	// continue passing the error, only error-handling middleware
	// would remain being executed, however here
	// we simply respond with an error page.

	var Gearman = require("node-gearman");
	var gearman = new Gearman(process.env.GEARMAN_MASTER || "localhost", process.env.GEARMAN_PORT || 4730, true);	
	gearman.connect();

	gearman.on("connect", function() {
    	console.log("Connected to gearman server!");
	});	

	var feed = require('./routes/feed')(gearman)


	app.use(function(err, req, res, next){
		// we may use properties of the error object
		// here and next(err) appropriately, or if
		// we possibly recovered from the error, simply next().
		mylogger.error('500 handler fired for error: '+err)
		mylogger.error(err.message)
		mylogger.error(err.stack)
		res.send('you just broke our server, man')
	});

	// development only
	if ('development' == app.get('env')) {
		app.use(express.errorHandler());
	}


	app.post('/feed', feed.new_feed)

	app.get('/server_status', function(req, res) {
		res.send({
			pid: process.pid,
			config: process.config,
			memory: process.memoryUsage(),
			uptime: process.uptime(),
			env: process.env
		})
	});	

	http.createServer(app).listen(app.get('port'), function(){
		mylogger.info('Express server listening on port ' + app.get('port'));
	});
}


process.on('uncaughtException', function (err) {
	mylogger.error('uncaughtException:', err.message)
	mylogger.error(err.stack)
	process.exit(1)
})
