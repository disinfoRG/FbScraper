from helper import helper

def get_comment_url(comment_node):
    permalink_node = None
    permalink_href = None
    
    url_selector = helper.data_testidify('UFI2CommentActionLinks/root')
    url_nodes = comment_node.select(url_selector)

    try:
        permalink_node = url_nodes[0].select('li:nth-child(3) > a')
        permalink_href = permalink_node[0].get('href')
    except NoSuchElementException:
        # url_node.get_attribute('innerHTML')
        # '<li class="_6coj"><span aria-hidden="true" class="_6cok">&nbsp;·&nbsp;</span><a class="_6qw7" data-ft="{&quot;tn&quot;:&quot;N&quot;}" href="https://www.facebook.com/eatnews/posts/470559583662483?comment_id=470610556990719"><abbr data-tooltip-content="2020年1月1日 星期三下午1:51" data-hover="tooltip" minimize="true" class="livetimestamp" data-utime="1577857868" data-minimize="true">1天</abbr></a></li>'
        # selenium.common.exceptions.NoSuchElementException: Message: no such element: Unable to locate element: {"method":"css selector","selector":"li:nth-child(3) > a"}
        # 'https://www.facebook.com/eatnews/posts/470559583662483?comment_id=470610556990719'
        permalink_href = url_nodes[0].select('a')[0].get('href')
    except Exception as e:
        Helper.print_error(e)
        pass

    return permalink_href