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
					},
					{
						queryObject: 'body',
						selector: ['blog_url'],
						fieldName: 'blog_url',
						constraints: [{
							'name': 'url',
							'value': ''
						}]
					}

				]
			}		
			jobber(requirements, res, gearman, 'new_feed')			
		},
		init_feed: function(req, res) {
			var requirements = {
				queryObjects: validate.pq_QO(req),
				requirements: [
					validate.uuid_REQ('feed_id', 'params')
				]
			}
			jobber(requirements, res, gearman, 'init_feed')
		},
		get_feed: function(req, res) {
			var requirements = {
				queryObjects: validate.pq_QO(req),
				requirements: [
					validate.uuid_REQ('feed_id', 'params')
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
		},
		feed_rules: function(req, res) {
			var requirements = {
				queryObjects: validate.bp_QO(req),
				requirements: [								
					{
						queryObject: 'body',
						selector: ['title'],
						fieldName: 'title',
						constraints: [{
							'name': 'lengthMin',
							'value': 1
						}]
					},
					{
						queryObject: 'body',
						selector: ['byline'],
						fieldName: 'byline',
						constraints: [{
							'name': 'lengthMin',
							'value': 1
						}]
					},
					{
						queryObject: 'body',
						selector: ['post_date'],
						fieldName: 'post_date',
						constraints: [{
							'name': 'lengthMin',
							'value': 1
						}]
					},
					{
						queryObject: 'body',
						selector: ['content'],
						fieldName: 'content',
						constraints: [{
							'name': 'lengthMin',
							'value': 1
						}]
					},
					{
						queryObject: 'body',
						selector: ['pagination'],
						fieldName: 'pagination',
						constraints: [{
							'name': 'lengthMin',
							'value': 1
						}]
					},
					{
						queryObject: 'body',
						selector: ['postlist'],
						fieldName: 'postlist',
						constraints: [{
							'name': 'lengthMin',
							'value': 1
						}]
					},
					validate.uuid_REQ('feed_id', 'params')
				]
			}		
			jobber(requirements, res, gearman, 'feed_rules')			
		}
	}
}