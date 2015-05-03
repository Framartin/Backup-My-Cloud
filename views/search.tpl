% setdefault('words', '')
% include('header.tpl', page='Search', bar_list_services = bar_list_services)
<div class="col-sm-9 col-sm-offset-3 col-md-10 col-md-offset-2 main">
  <div class="list-group">
    <h1 class="page-header">Results of the search of {{words}}</h1>
    {{ !message }}
    {{ !list_html }}
  </div>
</div>

% include('foother.tpl')
