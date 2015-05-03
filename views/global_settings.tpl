% setdefault('message', '')
% include('header.tpl', page='Settings', bar_list_services = bar_list_services)
<div class="col-sm-9 col-sm-offset-3 col-md-10 col-md-offset-2 main">
  <div class="list-group">
    <h1 class="page-header">Configure BackupMyCloud</h1>
{{ !message }}
<form class="form-horizontal" method="post">
  <h4 class="sub-header">Export format</h4>
  <div class="form-group">
    <label for="etherpad" class="col-sm-2 control-label">Etherpad (google docs like)</label>
    <div class="col-sm-offset-2 col-sm-10">
      <div class="radio">
        <label>
          <input type="radio" name="etherpad" value="txt" {{ 'checked' if config['format']['etherpad']=='txt' else '' }}>
          Text file (.txt)
        </label>
      </div>
      <div class="radio">
        <label>
          <input type="radio" name="etherpad" value="html" {{ 'checked' if config['format']['etherpad']=='html' else '' }}>
          HTML (.html)
        </label>
      </div>
      <div class="radio">
        <label>
          <input type="radio" name="etherpad" value="pdf" {{ 'checked' if config['format']['etherpad']=='pdf' else '' }}>
          PDF (.pdf)
        </label>
      </div>
      <div class="radio">
        <label>
          <input type="radio" name="etherpad" value="doc" {{ 'checked' if config['format']['etherpad']=='doc' else '' }}>
          DOC (.doc)
        </label>
      </div>
    </div>
  </div>
  <div class="form-group">
    <label for="framadate" class="col-sm-2 control-label">Framadate (doodle like)</label>
    <div class="col-sm-offset-2 col-sm-10">
      <div class="radio">
        <label>
          <input type="radio" name="framadate" value="csv" {{ 'checked' if config['format']['framadate']=='csv' else '' }}>
          CSV (.csv)
        </label>
      </div>
    </div>
  </div>
  <div class="form-group">
    <div class="col-sm-offset-2 col-sm-10">
      <button type="submit" class="btn btn-default">Save the configuration</button>
    </div>
  </div>
</form>
  </div>
</div>

% include('foother.tpl')
