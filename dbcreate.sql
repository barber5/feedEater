--
-- PostgreSQL database dump
--

-- Dumped from database version 9.3.2
-- Dumped by pg_dump version 9.3.1
-- Started on 2014-02-08 21:51:44 PST

SET statement_timeout = 0;
SET lock_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;

--
-- TOC entry 172 (class 3079 OID 11756)
-- Name: plpgsql; Type: EXTENSION; Schema: -; Owner: 
--

CREATE EXTENSION IF NOT EXISTS plpgsql WITH SCHEMA pg_catalog;


--
-- TOC entry 1985 (class 0 OID 0)
-- Dependencies: 172
-- Name: EXTENSION plpgsql; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION plpgsql IS 'PL/pgSQL procedural language';


--
-- TOC entry 173 (class 3079 OID 16770)
-- Name: pg_trgm; Type: EXTENSION; Schema: -; Owner: 
--

CREATE EXTENSION IF NOT EXISTS pg_trgm WITH SCHEMA public;


--
-- TOC entry 1986 (class 0 OID 0)
-- Dependencies: 173
-- Name: EXTENSION pg_trgm; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION pg_trgm IS 'text similarity measurement and index searching based on trigrams';


SET search_path = public, pg_catalog;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- TOC entry 170 (class 1259 OID 16821)
-- Name: feeds; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE feeds (
    id uuid NOT NULL,
    name character varying(255) NOT NULL,
    feed_url character varying(255),
    blog_url character varying(255) NOT NULL,
    extraction_rule character varying(1024),
    pagination_rule character varying(1024),
    last_crawl timestamp without time zone,
    created timestamp without time zone,
    updated timestamp without time zone,
    validated boolean DEFAULT true
);


ALTER TABLE public.feeds OWNER TO postgres;

--
-- TOC entry 171 (class 1259 OID 16829)
-- Name: posts; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE posts (
    id uuid NOT NULL,
    title character varying(255),
    feed_id uuid NOT NULL,
    byline character varying(1024),
    post_date timestamp without time zone,
    comment_feed character varying(255),
    post_url character varying(255),
    content text,
    created timestamp without time zone,
    updated timestamp without time zone
);


ALTER TABLE public.posts OWNER TO postgres;

--
-- TOC entry 1863 (class 2606 OID 16828)
-- Name: feeds_blog_url_key; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY feeds
    ADD CONSTRAINT feeds_blog_url_key UNIQUE (blog_url);


--
-- TOC entry 1865 (class 2606 OID 16840)
-- Name: feeds_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY feeds
    ADD CONSTRAINT feeds_pkey PRIMARY KEY (id);


--
-- TOC entry 1867 (class 2606 OID 16838)
-- Name: posts_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY posts
    ADD CONSTRAINT posts_pkey PRIMARY KEY (id);


--
-- TOC entry 1869 (class 2606 OID 16836)
-- Name: posts_post_url_key; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY posts
    ADD CONSTRAINT posts_post_url_key UNIQUE (post_url);


--
-- TOC entry 1870 (class 2606 OID 16841)
-- Name: fk_posts; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY posts
    ADD CONSTRAINT fk_posts FOREIGN KEY (feed_id) REFERENCES feeds(id) ON DELETE CASCADE;


--
-- TOC entry 1984 (class 0 OID 0)
-- Dependencies: 6
-- Name: public; Type: ACL; Schema: -; Owner: postgres
--

REVOKE ALL ON SCHEMA public FROM PUBLIC;
REVOKE ALL ON SCHEMA public FROM postgres;
GRANT ALL ON SCHEMA public TO postgres;
GRANT ALL ON SCHEMA public TO PUBLIC;


--
-- TOC entry 1987 (class 0 OID 0)
-- Dependencies: 170
-- Name: feeds; Type: ACL; Schema: public; Owner: postgres
--

REVOKE ALL ON TABLE feeds FROM PUBLIC;
REVOKE ALL ON TABLE feeds FROM postgres;
GRANT ALL ON TABLE feeds TO postgres;
GRANT ALL ON TABLE feeds TO feedman;


--
-- TOC entry 1988 (class 0 OID 0)
-- Dependencies: 171
-- Name: posts; Type: ACL; Schema: public; Owner: postgres
--

REVOKE ALL ON TABLE posts FROM PUBLIC;
REVOKE ALL ON TABLE posts FROM postgres;
GRANT ALL ON TABLE posts TO postgres;
GRANT ALL ON TABLE posts TO feedman;


-- Completed on 2014-02-08 21:51:57 PST

--
-- PostgreSQL database dump complete
--

