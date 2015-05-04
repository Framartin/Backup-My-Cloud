% setdefault('message', '')
% include('header.tpl', page='Batch', bar_list_services = bar_list_services)
<div class="col-sm-9 col-sm-offset-3 col-md-10 col-md-offset-2 main">
  <div class="list-group">
    <h1 class="page-header">Backup content in a batch</h1>
    {{ !message }}
    <p>Do you want to backup every content marked as auto-backup in one go?</p>
    <a href="auto_backup_ok" class="btn btn-primary btn-lg" role="button">Batch Backup!</a>
  </div>
</div>

% include('foother.tpl')
