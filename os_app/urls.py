from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from . import views

app_name = 'os_app'

urlpatterns = [
    # Autenticação
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Dashboard
    path('', views.index, name='index'),
    
    # Professores - CRUD Completo
    path('professores/', views.lista_professores, name='lista_professores'),
    path('professores/novo/', views.novo_professor, name='novo_professor'),
    path('professores/<int:pk>/', views.detalhe_professor, name='detalhe_professor'),
    path('professores/<int:pk>/editar/', views.editar_professor, name='editar_professor'),
    path('professores/<int:pk>/deletar/', views.deletar_professor, name='deletar_professor'),
    
    # AJAX - Carregar escolas por núcleo
    path('api/escolas/por-nucleo/', views.carregar_escolas_por_nucleo, name='carregar_escolas_por_nucleo'),
    
    # AJAX - Cadastros
    path('api/nucleo/novo/', views.nova_escola_nucleo_ajax, name='nova_escola_nucleo_ajax'),
    path('api/escola/nova/', views.nova_escola_ajax, name='nova_escola_ajax'),
    path('api/cargo/novo/', views.novo_cargo_ajax, name='novo_cargo_ajax'),
    path('api/bairro/buscar/', views.buscar_bairros_ajax, name='buscar_bairros_ajax'),
    path('api/bairro/novo/', views.novo_bairro_ajax, name='novo_bairro_ajax'),
    path('api/serie/nova/', views.nova_serie_ajax, name='nova_serie_ajax'),
    path('api/serie/listar/', views.listar_series_ajax, name='listar_series_ajax'),
    path('api/motivo/novo/', views.novo_motivo_ajax, name='novo_motivo_ajax'),
    path('api/motivo/listar/', views.listar_motivos_ajax, name='listar_motivos_ajax'),

    # Escolas Núcleo
    path('escolas-nucleo/', views.lista_escolas_nucleo, name='lista_escolas_nucleo'),
    path('escolas-nucleo/novo/', views.nova_escola_nucleo, name='nova_escola_nucleo'),
    path('escolas-nucleo/<int:pk>/editar/', views.editar_escola_nucleo, name='editar_escola_nucleo'),
    path('escolas-nucleo/<int:pk>/deletar/', views.deletar_escola_nucleo, name='deletar_escola_nucleo'),
    
    # Escolas Dependentes
    path('escolas-dependentes/', views.lista_escolas_dependentes, name='lista_escolas_dependentes'),
    path('escolas-dependentes/novo/', views.nova_escola_dependente, name='nova_escola_dependente'),
    path('escolas-dependentes/<int:pk>/editar/', views.editar_escola_dependente, name='editar_escola_dependente'),
    path('escolas-dependentes/<int:pk>/deletar/', views.deletar_escola_dependente, name='deletar_escola_dependente'),
    
    # AJAX - Busca de professores para substituição
    path('api/professores/buscar/', views.buscar_professores_ajax, name='buscar_professores_ajax'),

    path('relatorios/', views.relatorios_filtros, name='relatorios_filtros'),
    path('relatorios/resultado/', views.relatorios_resultado, name='relatorios_resultado'),
    path('relatorios/pdf/', views.relatorios_pdf, name='relatorios_pdf'),
    
    # Logs de Auditoria
    path('logs/', views.logs_auditoria, name='logs_auditoria'),
    path('logs/<int:log_id>/', views.log_detalhe, name='log_detalhe'),
    path('logs/meu-historico/', views.logs_meu_historico, name='logs_meu_historico'),
    path('logs/exportar/', views.logs_exportar, name='logs_exportar'),

    # Gestão de Usuários
    path('usuarios/', views.lista_usuarios, name='lista_usuarios'),
    path('usuarios/novo/', views.novo_usuario, name='novo_usuario'),
    path('usuarios/<int:user_id>/', views.detalhe_usuario, name='detalhe_usuario'),
    path('usuarios/<int:user_id>/editar/', views.editar_usuario, name='editar_usuario'),
    path('usuarios/<int:user_id>/senha/', views.alterar_senha, name='alterar_senha'),
    path('usuarios/<int:user_id>/desativar/', views.desativar_usuario, name='desativar_usuario'),
    
    # Perfil do usuário logado
    path('meu-perfil/', views.meu_perfil, name='meu_perfil'),
    path('minha-senha/', views.minha_senha, name='minha_senha'),

]

# Servir arquivos de mídia apenas em desenvolvimento
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)