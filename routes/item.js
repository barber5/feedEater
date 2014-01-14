var jobber = require('../util/jobber').jobber
var validate = require('../util/validate')

module.exports = function(gearman) {
	return {
		new_itemlist: function(req, res) {
			var requirements = {
				queryObjects: validate.bp_QO(req),
				requirements: [
					validate.name_REQ('body'),															
					validate.uuid_REQ('profile_id', 'params'),
					validate.access_token_REQ('body')
				]
			}		
			jobber(requirements, res, gearman, 'new_itemlist')			
		}	
	}
}