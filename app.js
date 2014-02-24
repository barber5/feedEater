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
	app.engine('html', require('ejs').renderFile);
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

	

	// development only
	if ('development' == app.get('env')) {
		app.use(express.errorHandler());
	}

	app.get('/', function(req, res) {
		res.render('index.html')
	})
	app.get('/feeds', feed.all_feeds)
	app.post('/feed', feed.new_feed)
	app.get('/feed/:feed_id', feed.get_feed)
	app.get('/feed/:feed_id/posts', feed.get_posts)
	app.post('/feed/:feed_id/test', feed.test_rule)
	app.post('/feed/:feed_id/init', feed.init_feed)
	app.post('/feed/:feed_id/crawl_posts', feed.crawl_all)
	app.post('/feed/:feed_id/rules', feed.feed_rules)
	app.get('/allcats', feed.all_categories)
	app.post('/post/:post_id/crawl', feed.crawl_post)
	app.post('/work', feed.crawl_work)
	app.post('/workmuch', feed.crawl_work_much)
	app.post('/category', feed.new_category)
	app.get('/post/:post_id', feed.get_post)
	app.get('/f/:feed_id', function(req, res) {
		res.render('feed.html', {feed_id: req.params.feed_id})
	})
	app.get('/newfeed', function(req, res) {
		res.render('newfeed.html')
	})
	app.get('/workadmin', function(req, res) {
		res.render('work.html')
	})
	app.get('/jobs', feed.get_jobs)

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
