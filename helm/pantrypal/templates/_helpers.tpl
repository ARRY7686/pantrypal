{{- define "pantrypal.name" -}}pantrypal{{- end }}

{{- define "pantrypal.fullname" -}}
{{- if contains "pantrypal" .Release.Name }}{{ .Release.Name | trunc 50 | trimSuffix "-" }}{{ else }}{{ printf "%s-pantrypal" .Release.Name | trunc 50 | trimSuffix "-" }}{{ end }}
{{- end }}

{{- define "pantrypal.labels" -}}
app.kubernetes.io/name: {{ include "pantrypal.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
helm.sh/chart: {{ printf "%s-%s" .Chart.Name .Chart.Version }}
{{- end }}

{{- define "pantrypal.selector" -}}
app.kubernetes.io/name: {{ include "pantrypal.name" .root }}
app.kubernetes.io/instance: {{ .root.Release.Name }}
app.kubernetes.io/component: {{ .component }}
{{- end }}

{{- define "pantrypal.image" -}}
{{- $registry := .root.Values.image.registry -}}
{{- if $registry }}{{ printf "%s/%s:%s" $registry .image.repository (toString .image.tag) }}{{ else }}{{ printf "%s:%s" .image.repository (toString .image.tag) }}{{ end }}
{{- end }}

{{- define "pantrypal.databaseUrl" -}}
postgresql+psycopg://$(POSTGRES_USER):$(POSTGRES_PASSWORD)@{{ include "pantrypal.fullname" . }}-postgres:5432/$(POSTGRES_DB)
{{- end }}
