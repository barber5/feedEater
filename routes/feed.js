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
		}	
	}
}