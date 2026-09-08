{{- define "jc-kubescale.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{- define "jc-kubescale.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{- define "jc-kubescale.labels" -}}
helm.sh/chart: {{ include "jc-kubescale.name" . }}-{{ .Chart.Version | replace "+" "_" }}
{{ include "jc-kubescale.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{- define "jc-kubescale.selectorLabels" -}}
app.kubernetes.io/name: {{ include "jc-kubescale.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}