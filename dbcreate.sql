--
-- PostgreSQL database dump
--

-- Dumped from database version 9.2.5
-- Dumped by pg_dump version 9.3.1
-- Started on 2013-12-03 19:12:44 PST

SET statement_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;

--
-- TOC entry 184 (class 3079 OID 12595)
-- Name: plpgsql; Type: EXTENSION; Schema: -; Owner: 
--

CREATE EXTENSION IF NOT EXISTS plpgsql WITH SCHEMA pg_catalog;
CREATE EXTENSION pg_trgm;

--
-- TOC entry 2903 (class 0 OID 0)
-- Dependencies: 184
-- Name: EXTENSION plpgsql; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION plpgsql IS 'PL/pgSQL procedural language';


SET search_path = public, pg_catalog;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- TOC entry 174 (class 1259 OID 16668)
-- Name: communities; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

DROP database if exists feed_eater;

CREATE DATABASE feed_eater
  WITH OWNER = postgres
       ENCODING = 'UTF8'
       TABLESPACE = pg_default
       LC_COLLATE = 'en_US.UTF-8'
       LC_CTYPE = 'en_US.UTF-8'
       CONNECTION LIMIT = -1       
       TEMPLATE template0;
\connect feed_eater
CREATE EXTENSION pg_trgm;

--
-- TOC entry 168 (class 1259 OID 17050)
-- Name: communities; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE feeds (
    id uuid NOT NULL,
    name character varying(255) NOT NULL,
    feed_url character varying(255) NOT NULL,
    blog_url character varying(255),
    extraction_rule character varying(1024),
    pagination_rule character varying(1024),
    created timestamp without time zone,
    updated timestamp without time zone,    
);


ALTER TABLE public.feeds OWNER TO postgres;

CREATE TABLE posts (
    id uuid NOT NULL,
    title character varying(255) NOT NULL,
    feed_id uuid NOT NULL,
    byline character varying(1024),
    post_date timestamp without time zone,
    comment_feed character varying(255),
    post_url character varying(255),
    content text,    
    created timestamp without time zone,
    updated timestamp without time zone,    
);


ALTER TABLE public.posts OWNER TO postgres;


ALTER TABLE ONLY posts
    ADD CONSTRAINT posts_pkey PRIMARY KEY (id);

ALTER TABLE ONLY posts
    ADD CONSTRAINT fk_posts FOREIGN KEY (feed_id) REFERENCES feeds(id) ON DELETE CASCADE;

ALTER TABLE ONLY feeds
    ADD CONSTRAINT feeds_pkey PRIMARY KEY (id);

--
-- TOC entry 2946 (class 0 OID 0)
-- Dependencies: 6
-- Name: public; Type: ACL; Schema: -; Owner: postgres
--

REVOKE ALL ON SCHEMA public FROM PUBLIC;
REVOKE ALL ON SCHEMA public FROM postgres;
GRANT ALL ON SCHEMA public TO postgres;
GRANT ALL ON SCHEMA public TO PUBLIC;

