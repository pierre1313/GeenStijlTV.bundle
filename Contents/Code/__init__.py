import re, string, datetime

####################################################################################################

PLUGIN_TITLE   = "GeenStijl.TV"
PLUGIN_PREFIX  = "/video/geenstijltv"

# URLS
URL_ROOT_URI       = "http://www.geenstijl.tv/"
URL_HOME           = URL_ROOT_URI + ""
URL_ARCHIEF        = URL_ROOT_URI + "archief.html"
URL_ZOEKEN         = URL_ROOT_URI + "fastsearch?query="

# OTHER VARS
CACHE_INTERVAL = 3600

# REGULAR EXPRESSIONS
REGEX_PAGE_ITEM = r"""<div class="article" id="entry-([0-9]+)">\s+(\s*<!-- google_ad_section_start -->\s*)?<h2>([^<]+)</h2>\s+<p><a href="([^<]+)" class="filmtease"><img src="([^<]+)" alt="([^<]+)" title="([^<]+)" /></a>\s+(<p>)?([^<]+)</p>""" #
REGEX_ARCHIVE_MONTH = r"""<li><a href="(http://www.geenstijl.tv/([0-9]+)/([0-9]+)/)">([^<]+)</a></li>"""
REGEX_ARCHIVE_ITEM = r"""<div class="artikel">\s+<div class="gstvfoto"><a href="([^<]+)"><img src="([^<]+)" alt="[^<]+" title="[^<]+" /></a></div>\s+<h4><a href="[^<]+">([^<]+)</a></h4>\s+(.*?)<p class="footer">"""
REGEX_SEARCH = r"""<li>\s+<a href="([^<]+)">([^<]+)</a>\s+<p>([^<]+)</p>"""
REGEX_STREAM1 = r"""xgstvplayer\('([^']+)'"""
REGEX_STREAM2 = r"""gstvplayer\('[0-9]+', '([^']+)'"""

REGEX_COMMENTS = r"""<a name="c[0-9]+"></a>\s+<div class="comment" id="c[0-9]+">\s+<p>(.*?)</p>\s+<p class="footer">([^|]+)"""

# Default artwork and icon(s)
PLUGIN_ARTWORK = "art-default.png"
PLUGIN_ICON_DEFAULT = "icon-default.png"
PLUGIN_ICON_ARCHIVE = "icon-archive.png"
PLUGIN_ICON_RECENT = "icon-recent.png"
PLUGIN_ICON_ZOEKEN = "icon-zoeken.png"
PLUGIN_ICON_SETTINGS = "icon-settings.png"
PLUGIN_ICON_HELP = "icon-help.png"
PLUGIN_ICON_NEXT = "icon-next.png"

####################################################################################################

def Start():
  Plugin.AddPrefixHandler(PLUGIN_PREFIX, MainMenu, PLUGIN_TITLE, PLUGIN_ICON_DEFAULT, PLUGIN_ARTWORK)

  Plugin.AddViewGroup("List", viewMode="List", mediaType="items")
  Plugin.AddViewGroup("Details", viewMode="InfoList", mediaType="items")

  # Set the default MediaContainer attributes
  MediaContainer.title1 = PLUGIN_TITLE
  MediaContainer.viewGroup = 'List'
  MediaContainer.art = R('art-default.jpg')

  # Set the default cache time
  HTTP.CacheTime = CACHE_INTERVAL

####################################################################################################

def MainMenu():
    dir = MediaContainer(noCache=True) 
    dir.Append(Function(DirectoryItem(HomePage, title="Laatse vijf afleveringen", thumb=R(PLUGIN_ICON_RECENT), art=R(PLUGIN_ARTWORK)), pageUrl = URL_HOME))
    dir.Append(Function(DirectoryItem(ArchivePage, title="Archief", thumb=R(PLUGIN_ICON_ARCHIVE), art=R(PLUGIN_ARTWORK)), pageUrl = URL_ARCHIEF))
    dir.Append(Function(InputDirectoryItem(SearchPage, title="Zoeken", thumb=R(PLUGIN_ICON_ZOEKEN), art=R(PLUGIN_ARTWORK), prompt="Zoeken"), pageUrl = URL_ZOEKEN))
    dir.Append(PrefsItem(title="Instellingen", thumb=R(PLUGIN_ICON_SETTINGS), art=R(PLUGIN_ARTWORK)))
    dir.Append(Function(DirectoryItem(AboutPage, title="Help", thumb=R(PLUGIN_ICON_HELP), art=R(PLUGIN_ARTWORK))))
 
    return dir

####################################################################################################

def AboutPage(sender):
  return MessageContainer("Help", "Een klein gedeelte van het archief staat in Silverlight. Dit wordt niet\ndoor deze plugin ondersteund, je krijgt dan de melding 'Could not\nread from input format'.")

####################################################################################################

def HomePage(sender, pageUrl):

  title = sender.itemTitle
  dir = MediaContainer(title2=title, noCache=True, art=R(PLUGIN_ARTWORK))
  dir.viewGroup = 'Details'
  dir = ParseHomePage(dir, pageUrl, REGEX_PAGE_ITEM)
  return dir

####################################################################################################

def ArchivePage(sender, pageUrl):

  title = sender.itemTitle
  dir = MediaContainer(title2=title, noCache=True, art=R(PLUGIN_ARTWORK))
  dir.viewGroup = 'List'
  dir = ParseArchivePage(dir, pageUrl, REGEX_ARCHIVE_MONTH)
  return dir

####################################################################################################

def SearchPage(sender, pageUrl, query):

  title = sender.itemTitle
  dir = MediaContainer(title2=title, noCache=True, art=R(PLUGIN_ARTWORK))
  dir.viewGroup = 'List'

  keywords = query.replace(" ", "%20")
  pageUrl = pageUrl + keywords 
 

  dir = ParseSearchPage(dir, pageUrl, REGEX_SEARCH)
  return dir

####################################################################################################

def ParseHomePage(dir, url, regex):
  data = HTTP.Request(url).content.decode('latin-1')

  results = re.compile(regex, re.DOTALL + re.IGNORECASE + re.M).findall(data)

  for result in results:
    if Prefs['comments'] == "aan":
      dir.Append(Function(DirectoryItem(OpenItem, title=result[2], thumb=result[4], summary=result[8]), title=result[2], thumb=result[4], summary=result[8], url=result[3]))
    else:
      dir.Append(Function(VideoItem(PlayVideo, title=result[2], thumb=result[4], summary=result[8]), url=result[3]))

  return dir

####################################################################################################

def ParseArchivePage(dir, url, regex):
  data = HTTP.Request(url).content.decode('latin-1')

  results = re.compile(regex, re.DOTALL + re.IGNORECASE + re.M).findall(data)

  for result in results:
    dir.Append(Function(DirectoryItem(OpenArchiveMonthItem, title=result[3], thumb=R(PLUGIN_ICON_ARCHIVE)), title=result[3], url=result[0]))

  return dir

####################################################################################################

def ParseSearchPage(dir, url, regex):
  data = HTTP.Request(url).content.decode('latin-1')
  data = data.replace('<b style="color:black;background-color:#FFFF00">', "")
  data = data.replace('<b style="color:black;background-color:#00FFFF">', "")
  data = data.replace('<b style="color:black;background-color:#00FFFF">', "")
  data = data.replace('<b style="color:black;background-color:#FF9999">', "")
  data = data.replace('<b style="color:black;background-color:#FF66FF">', "")
  data = data.replace('</b>', "")

  results = re.compile(regex, re.DOTALL + re.IGNORECASE + re.M).findall(data)

  for result in results:
    if Prefs['comments'] == "aan":
      dir.Append(Function(DirectoryItem(OpenItem, title=result[1], thumb=R(PLUGIN_ICON_DEFAULT), summary=result[2]), title=result[1], thumb=R(PLUGIN_ICON_DEFAULT), summary=result[2], url=result[0]))
    else:
      dir.Append(Function(VideoItem(PlayVideo, title=result[1], thumb=R(PLUGIN_ICON_DEFAULT), summary=result[2]), url=result[0]))


  if len(dir) == 0:
    dir = MessageContainer('Zoeken',"geen resultaten ... ")
  return dir

####################################################################################################

def OpenArchiveMonthItem(sender, title, url):
  dir = MediaContainer(title2=title, noCache=True, art=R(PLUGIN_ARTWORK))
  dir.viewGroup = 'Details'
 
  data = HTTP.Request(url).content.decode('latin-1')
  results = re.compile(REGEX_ARCHIVE_ITEM, re.DOTALL + re.IGNORECASE + re.M).findall(data)
  
  for result in results:
    if Prefs['comments'] == "aan":
      dir.Append(Function(DirectoryItem(OpenItem, title=result[2], summary=result[3], thumb=result[1]), title=result[2], summary=result[3], thumb=result[1], url=result[0]))
    else:
      dir.Append(Function(VideoItem(PlayVideo, title=result[2], thumb=result[1], summary=result[3]), url=result[0]))

  return dir

####################################################################################################

def OpenItem(sender, title, summary, thumb, url):
  dir = MediaContainer(title2=title, noCache=True, art=R(PLUGIN_ARTWORK))
  dir.viewGroup = 'Details'

  #play button
  dir.Append(Function(VideoItem(PlayVideo, title="Play", summary=title+"\n\n"+summary, thumb=thumb), url=url)) 

  #append comments
  dir = ParseComments(dir, url, REGEX_COMMENTS, thumb)

  return dir

####################################################################################################

def ParseComments(dir, url, regex, thumb):
	
  data = HTTP.Request(url).content.decode('latin-1')
  results = re.compile(regex, re.DOTALL + re.IGNORECASE + re.M).findall(data)

  dir.Append(DirectoryItem("none", title="", thumb=thumb))
  dir.Append(DirectoryItem("none", title="Comments ("+str(len(results))+")", thumb=thumb))

  for result in results:
    name = result[1]+": "+result[0]
    name = name.replace(".", "")
    name = name.replace("?", "")
    name = name.replace("\\", "")
    name = name.replace("  ", " ")
    name = name.replace('<span class="baby" title="newbie"></span>', '')
    name = name.replace('<p>', '')
    name = name.replace('</p>', '')
    name = name.replace('<br />', '')
    name = name.replace('<br/>', '')
    name = name.replace('\n', ' ')
    name = "   - "+name[:30]
    if len(name) > 30: name = name+"..."
	
    summary = result[0]
    summary = summary.replace('<p>', '')
    summary = summary.replace('</p>', '')
    summary = summary.replace('<br />', '')
    summary = summary.replace('<br/>', '')
    dir.Append(DirectoryItem("none", title=name, subtitle=result[1], thumb=thumb, summary=summary))

  return dir

####################################################################################################

def PlayVideo(sender, url):

  url = StreamUrl(url)

  if url=="":
    return None
  else:
	return Redirect(url)

####################################################################################################

def StreamUrl(url):
  stream = ""
  data = HTTP.Request(url).content.decode('latin-1')

  results_video = re.compile(REGEX_STREAM1, re.DOTALL + re.IGNORECASE + re.M).findall(data)
  for result_video in results_video:
    stream = result_video

  if stream == "":
    results_video = re.compile(REGEX_STREAM2, re.DOTALL + re.IGNORECASE + re.M).findall(data)
    for result_video in results_video:
      stream = result_video

  return stream
