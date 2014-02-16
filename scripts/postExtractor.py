from util import extractPost, extractPosts, getNextPage
import sys, urlparse

if __name__ == "__main__":
	post_rule = {
        'title':  'h1.entry-title',
        'byline': 'div.post-meta > span.author',
        'post_date': 'div.post-meta > a > span.timestamp',
        'content': 'div.post-entry',
        'postlist': 'h1.entry-title > a'
    }
	page_rule = 'div.previous > a'
	posts = extractPosts(post_rule, sys.argv[1])
	print 'got first page of posts'
	print posts
	np = urlparse.urljoin(sys.argv[1], getNextPage(page_rule, sys.argv[1]))
	posts = (extractPosts(post_rule, np))
	print 'got second page of posts'
	print posts
	np = urlparse.urljoin(np, getNextPage(page_rule, np))
	posts = extractPosts(post_rule, np)
	print 'got third page of posts'
	print posts
	if len(posts) > 0:
		print 'and a typical post is: '
		print extractPost(posts[0], post_rule)
