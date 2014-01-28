var jobber = require('../util/jobber').jobber
var validate = require('../util/validate')

module.exports = function(gearman) {
	return {
		new_feed: function(req, res) {
			var requirements = {
				queryObjects: validate.bp_QO(req),
				requirements: [
					validate.name_REQ('body'),	
					{
						queryObject: 'body',
						selector: ['feed_url'],
						fieldName: 'feed_url',
						constraints: [{
							'name': 'url',
							'value': ''
						}]
					}																			
				]
			}		
			jobber(requirements, res, gearman, 'new_feed')			
		},
		crawl_feed: function(req, res) {
			var requirements = {
				queryObjects: validate.pq_QO(req),
				requirements: [
					validate.UUID_REQ('params', 'feed_id')
				]
			}
			jobber(requirements, res, gearman, 'crawl_feed')
		},
		get_feed: function(req, res) {
			var requirements = {
				queryObjects: validate.pq_QO(req),
				requirements: [
					validate.UUID_REQ('params', 'feed_id')
				]
			}
			jobber(requirements, res, gearman, 'get_feed')
		},
		all_feeds: function(req, res) {
			var requirements = {
				queryObjects: validate.q_QO(req),
				requirements: [
					validate.limit_REQ
				]
			}
			jobber(requirements, res, gearman, 'all_feeds')
		}
	}
}