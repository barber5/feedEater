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
		new_category: function(req, res) {
			var requirements = {
				queryObjects: validate.bp_QO(req),
				requirements: [
					validate.name_REQ('body')
				]
			}		
			jobber(requirements, res, gearman, 'new_category')			
		},
		all_categories: function(req, res) {
			var requirements = {
				queryObjects: validate.bp_QO(req),
				requirements: [
				]
			}		
			jobber(requirements, res, gearman, 'all_categories')	
		},
		get_jobs: function(req, res) {
			var requirements = {
				queryObjects: validate.bp_QO(req),
				requirements: [
				]
			}		
			jobber(requirements, res, gearman, 'get_jobs')
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
		test_rule: function(req, res) {
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
						selector: ['comment'],
						fieldName: 'comment',
						isOptional: true,
						constraints: []
					},
					{
						queryObject: 'body',
						selector: ['blogroll'],
						fieldName: 'blogroll',
						isOptional: true,
						constraints: []
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
			jobber(requirements, res, gearman, 'test_rule')			
		},
		get_posts: function(req, res) {
			var requirements = {
				queryObjects: validate.pq_QO(req),
				requirements: [
					validate.uuid_REQ('feed_id', 'params')
				]
			}
			jobber(requirements, res, gearman, 'get_posts')
		},
		get_post: function(req, res) {
			var requirements = {
				queryObjects: validate.pq_QO(req),
				requirements: [
					validate.uuid_REQ('post_id', 'params')
				]
			}
			jobber(requirements, res, gearman, 'get_post')
		},
		crawl_all: function(req, res) {
			var requirements = {
				queryObjects: validate.pq_QO(req),
				requirements: [
					validate.uuid_REQ('feed_id', 'params')
				]
			}
			jobber(requirements, res, gearman, 'crawl_all')
		},
		crawl_post: function(req, res) {
			var requirements = {
				queryObjects: validate.pq_QO(req),
				requirements: [
					validate.uuid_REQ('post_id', 'params')
				]
			}
			jobber(requirements, res, gearman, 'crawl_post')
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
		crawl_work: function(req, res) {
			var requirements = {
				queryObjects: validate.b_QO(req),
				requirements: [	
					validate.uuid_REQ('resId', 'body', true)	,
					{
						queryObject: 'body',
						selector: ['domain'],
						fieldName: 'domain',
						isOptional: true,
						constraints: [{
							'name': 'lengthMin',
							'value': 1
						}]
					}			
				]
			}
			jobber(requirements, res, gearman, 'crawl_work')
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
						selector: ['comment'],
						fieldName: 'comment',
						isOptional: true,
						constraints: []
					},
					{
						queryObject: 'body',
						selector: ['blogroll'],
						fieldName: 'blogroll',
						isOptional: true,
						constraints: []
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